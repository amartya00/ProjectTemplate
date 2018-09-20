"""
This module is responsible for creating a snap part. This is the same thing that is used as dependencies while building
the project.

This creates a tar archive. The contents of the archive are as follows:
1. Some libraries (can be any kind of file)
2. An auto-generated CMakeLists.txt. This contains scripts to bootstrap the dependencies and also for building the snap.
3. A `md.json` file. This is auto-generated from the package's own md.json by extracting oy=ut the dependencies section.

This module needs the following config parameters:
1. ProjectRoot (This is the root relative to which we find the headers)
2. BuildFolder (This is the root relative to which we find the libs)
3. PartType (This defines whether we want to build a headers part or libs part)
4. LibNames (Needed if PartType == lib)
5. HeadersSource (Needed if PartType == headers)
6. HeadersDest (Needed if PartType == headers)

NOTE:
    No exceptions are thrown in the constructor to enable creation of an onject even if packaging info is absent in md.
"""
import os
import tarfile
import json
import tempfile


class SnapPartException (Exception):
    pass


class SnapPart:
    def __init__(self, config):
        try:
            self.config = config
            self.logger = config["Logger"]
        except KeyError as e:
            raise SnapPartException(e)

    def gather_libs(self, src_folder, file_list):
        retval = []
        try:
            self.logger.info("Scanning folder " + src_folder + " for libraries.")
            contents = os.listdir(src_folder)
            for entry in contents:
                full_path = os.path.join(src_folder, entry)
                if entry in file_list:
                    self.logger.info("Found library " + entry)
                    retval.append(full_path)
                elif os.path.isdir(full_path):
                    retval.extend(self.gather_libs(full_path, file_list))
            return retval
        except OSError as e:
            self.logger.error(str(e))
            raise SnapPartException(e)

    def generate_meta_data(self):
        md = {
            "Dependencies": []
        }
        if "Dependencies" in self.config:
            md["Dependencies"].extend(self.config["Dependencies"])
        if "RuntimeDeps" in self.config:
            md["Dependencies"].extend(self.config["RuntimeDeps"])
        if "BuildDeps" in self.config:
            md["Dependencies"].extend(self.config["BuildDeps"])
        if "TestDeps" in self.config:
            md["Dependencies"].extend(self.config["TestDeps"])
        return json.dumps(md, indent=4)

    def generate_cmake_lists(self):
        # Part type defines header vs lib
        install_target = self.config["PartType"]
        cmake_str = "cmake_minimum_required(VERSION 3.0)\n"

        if install_target.lower() == "lib":
            # A lib part type requires a list of files / libs to copy
            if "LibNames" not in self.config:
                raise SnapPartException("A lib part type needs a LibNames parameter in packaging information.")
            cmake_str = cmake_str + "project(" + self.config["Name"] + ")\n"

            for lib in self.config["LibNames"]:
                cmake_str = cmake_str + "file(GLOB libs ${CMAKE_CURRENT_SOURCE_DIR}/" + lib + ")\n"
            cmake_str = cmake_str + "install(FILES ${libs} DESTINATION lib)"

        elif install_target.lower() == "headers":
            if "HeadersDest" not in self.config:
                raise SnapPartException("Need a \"HeadersSource\" parameter indicating where to copy the headers to.")
            dest = self.config["HeadersDest"]
            cmake_str = cmake_str + "project(" + self.config["Name"] + ")\n"
            cmake_str = cmake_str + "install(DIRECTORY " + dest + " DESTINATION headers USE_SOURCE_PERMISSIONS)"
        return cmake_str

    def generate_archive_libs(self):
        cmake_str = self.generate_cmake_lists()
        md_str = self.generate_meta_data()
        if not os.path.isdir(self.config["BuildFolder"]):
            raise SnapPartException("Could not find build folder. Please build first before attempting to package.")
        all_libs = self.gather_libs(
            src_folder=self.config["BuildFolder"],
            file_list=self.config["LibNames"])
        if len(all_libs) != len(self.config["LibNames"]):
            raise SnapPartException("Could not find all libraries.")

        archive_name = os.path.join(self.config["BuildFolder"], self.config["Name"] + ".tar")
        with tarfile.open(archive_name, "w") as tfp:
            # Add CMakeLists.txt
            with tempfile.NamedTemporaryFile(mode="w") as cmake_file:
                cmake_file.write(cmake_str)
                cmake_file.flush()
                tfp.add(cmake_file.name, arcname="CMakeLists.txt")

            # Add md.json
            with tempfile.NamedTemporaryFile(mode="w") as md_file:
                md_file.write(md_str)
                md_file.flush()
                tfp.add(md_file.name, arcname="md.json")

            # Add libs to archive
            for lib in all_libs:
                tfp.add(lib, arcname=lib.split("/")[-1])

        self.logger.info("Done building library based snap part.")
        return self

    def find_headers_source(self, root, headers_src):
        contents = os.listdir(root)
        for entry in contents:
            full_path = os.path.join(root, entry)
            if entry == os.path.basename(self.config["LocalPackageCache"]):
                continue
            elif entry == headers_src:
                return os.path.join(root, entry)
            elif os.path.isdir(full_path):
                retval = self.find_headers_source(full_path, headers_src)
                if retval is not None:
                    return retval
        return None

    def generate_archive_headers(self):
        self.logger.info("Building snap part header.")
        if "HeadersSource" not in self.config:
            raise SnapPartException("Expecting \"HeadersSource\" to be present in snap part conf.")
        if "HeadersDest" not in self.config:
            raise SnapPartException("Expecting \"HeadersDest\" to be present in snap part conf.")
        headers_src = self.find_headers_source(self.config["ProjectRoot"], self.config["HeadersSource"])
        if headers_src is None:
            raise SnapPartException("Could not find headers source (" + self.config["HeadersSource"] + ").")
        cmake_str = self.generate_cmake_lists()
        md_str = self.generate_meta_data()

        archive_name = os.path.join(self.config["BuildFolder"], self.config["Name"] + ".tar")
        with tarfile.open(archive_name, "w") as tfp:
            # Add cMakeLists.txt
            with tempfile.NamedTemporaryFile(mode="w") as cmake_file:
                cmake_file.write(cmake_str)
                cmake_file.flush()
                tfp.add(cmake_file.name, arcname="CMakeLists.txt")

            # Add md.json
            with tempfile.NamedTemporaryFile(mode="w") as md_file:
                md_file.write(md_str)
                md_file.flush()
                tfp.add(md_file.name, arcname="md.json")

            # Add the headers folder
            tfp.add(headers_src, arcname=self.config["HeadersDest"])

        self.logger.info("Done building snap part headers.")
        return self

    def generate_snap_part(self):
        if "PartType" not in self.config:
            raise SnapPartException("Expecting \"PartType\" parameter in snap part config.")
        part_type = self.config["PartType"]
        if part_type == "lib":
            try:
                self.generate_archive_libs()
            except OSError as e:
                raise (SnapPartException(str(e)))
        elif part_type == "headers":
            try:
                self.generate_archive_headers()
            except OSError as e:
                raise (SnapPartException(str(e)))
        else:
            raise SnapPartException("Invalid part type. Allowed values are:  \"lib\" and \"headers\".")
