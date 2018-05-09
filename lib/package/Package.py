"""
Class: Package
Configuration parameters needed:
1. LocalPackageCache
2. PackageCacheRoot
3. BucketName
4. ProjectDir
5. BuildFolder
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import traceback

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")
sys.dont_write_bytecode = True

from lib.build.DependencyResolver import DependencyResolver
from lib.build.PackageDownloader import PackageDownloader


class PackageException(Exception):
    def __init__(self, message="Unknown exception"):
        self.message = message

    def __str__(self):
        return self.message


class Package:
    def __init__(self, conf, logger):
        if not os.path.isfile(os.path.join(os.getcwd(), "md.json")):
            raise PackageException("Expecting md.json present in PWD.")
        with open("md.json", "r") as fp:
            md = json.loads(fp.read())
        self.md = md
        self.conf = conf
        self.logger = logger
        if not os.path.isdir(self.conf["LocalPackageCache"]):
            raise PackageException("Local package cache absent. Please build the damn project first.")
        self.dependency_list = json.loads(
            open(
                os.path.join(self.conf["LocalPackageCache"], DependencyResolver.DEPENDENCY_FILE), "r"
            ).read()
        )

    @staticmethod
    def recursive_file_search(root, fname):
        files = os.listdir(root)
        for f in files:
            if os.path.isfile(os.path.join(root, f)) and f == fname:
                return os.path.join(root, f)
            if os.path.isdir(os.path.join(root, f)):
                result = Package.recursive_file_search(os.path.join(root, f), fname)
                if result:
                    return result
        return None

    def get_package_path(self, package_name, package_version):
        tar_folder = os.path.join(self.conf["PackageCacheRoot"], os.path.join(package_name, package_version))
        local_path = os.path.join(tar_folder, package_name + ".tar")
        if os.path.isfile(local_path):
            return local_path
        remote_path = PackageDownloader.get_s3_url(self.conf["BucketName"], package_name, package_version)
        return remote_path

    @staticmethod
    def make_cmake_lists_for_snap_part(snap_part_conf):
        install_target = snap_part_conf["PartType"]
        cmake_str = "cmake_minimum_required(VERSION 3.0)\n"
        if install_target == "lib":
            if "LibName" not in snap_part_conf:
                raise PackageException("A lib part type needs a LibName parameter in packaging information.")
            cmake_str = cmake_str + "project(" + snap_part_conf["Name"] + ")\n"
            cmake_str = cmake_str + "file(GLOB libs ${CMAKE_CURRENT_SOURCE_DIR}/*.so*)\n"
            cmake_str = cmake_str + "file(GLOB libs ${CMAKE_CURRENT_SOURCE_DIR}/*.a*)\n"
            cmake_str = cmake_str + "install(FILES ${libs} DESTINATION lib)"
        elif install_target == "headers":
            if "HeadersSource" not in snap_part_conf:
                raise PackageException("Need a headers folder to create a header based snap-part.")
            if "HeadersDest" not in snap_part_conf:
                raise PackageException("Need a headers folder to create a header based snap-part.")
            cmake_str = cmake_str + "project(" + snap_part_conf["Name"] + ")\n"
            cmake_str = cmake_str + "install(DIRECTORY " + snap_part_conf[
                "HeadersDest"] + " DESTINATION headers USE_SOURCE_PERMISSIONS)"
        return cmake_str

    def snappy_yaml(self, snappy):
        self.logger.info("Creating snappy yaml.")
        # Package metadata
        yamlstr = "name: " + snappy["Name"] + "\n"
        yamlstr = yamlstr + "version: " + "'" + snappy["Version"] + "'\n"
        yamlstr = yamlstr + "summary: " + snappy["Summary"] + "\n"
        yamlstr = yamlstr + "grade: " + snappy["Grade"] + "\n"
        yamlstr = yamlstr + "confinement: " + snappy["Confinement"] + "\n"
        yamlstr = yamlstr + "description: " + snappy["Description"] + "\n\n"
        yamlstr = yamlstr + "apps:\n"
        for a in snappy["Apps"]:
            yamlstr = yamlstr + "  " + a["Name"] + ":\n"
            yamlstr = yamlstr + "    command: " + a["Command"] + "\n\n"

        # Dependencies
        yamlstr = yamlstr + "parts:\n"
        for d in self.dependency_list:
            package_name = d["Package"]
            package_version = d["Version"]
            yamlstr = yamlstr + "  " + package_name + ":\n"
            yamlstr = yamlstr + "    plugin: cmake\n"
            yamlstr = yamlstr + "    source: " + self.get_package_path(package_name, package_version) + "\n\n"
        yamlstr = yamlstr + "  " + snappy["Name"] + ":\n"
        yamlstr = yamlstr + "    plugin: cmake\n"
        yamlstr = yamlstr + "    source: " + self.conf["ProjectDir"] + "\n"
        yamlstr = yamlstr + "    configflags: [-DPACKAGE_CACHE=" + self.conf["LocalPackageCache"] + "]\n\n"
        self.logger.info(yamlstr)
        return yamlstr

    def make_snap(self, snappy):
        self.logger.info("Building snap.")
        with tempfile.TemporaryDirectory() as temp_folder:
            snap_folder = os.path.join(temp_folder, "snap")
            os.makedirs(snap_folder)
            with open(os.path.join(snap_folder, "snapcraft.yaml"), "w") as fp:
                fp.write(self.snappy_yaml(snappy))
                self.logger.info("Created snapcraft.yaml in temporary folder: " + snap_folder)
            cwd = os.getcwd()
            os.chdir(temp_folder)
            p = subprocess.Popen(["snapcraft"])
            p.communicate()
            if not p.returncode == 0:
                self.logger.error("Building snap failed.")
            else:
                self.logger.info("Built snap in folder: " + temp_folder)
                for s in os.listdir(temp_folder):
                    if s.endswith(".snap"):
                        shutil.copyfile(os.path.join(temp_folder, s), os.path.join(self.conf["BuildFolder"], s))
                        self.logger.info("Copied the snap to: " + os.path.join(self.conf["BuildFolder"], s))
                        self.logger.info("Finshed snap building process.")
            os.chdir(cwd)
            self.logger.info("Done building snap.")
        return self

    def make_snap_part_lib(self, snap_part_conf):
        self.logger.info("Building snap part library.")
        if not "LibName" in snap_part_conf:
            raise PackageException("Expecting 'LibName' to be present in snap part conf.")
        if not "Name" in snap_part_conf:
            raise PackageException("Expecting 'Name' to be present in snap part conf.")
        # Create the CmakeLists.txt
        cmake_lists_txt = Package.make_cmake_lists_for_snap_part(snap_part_conf)
        self.logger.info("Snap lib CMakeLists.txt: ")
        self.logger.info(cmake_lists_txt)

        # Find the assoiated library
        if not os.path.isdir(self.conf["BuildFolder"]):
            raise PackageException(
                "Could not find build folder while trying to build snap part (lib). Make sure the code is built.")
        lib_path = Package.recursive_file_search(self.conf["BuildFolder"], snap_part_conf["LibName"])
        if not lib_path:
            raise PackageException("Could not find library " + snap_part_conf["LibName"] + " in build folder.")
        with tarfile.open(os.path.join(self.conf["BuildFolder"], snap_part_conf["Name"] + ".tar"), "w") as tfp:
            tfp.add(lib_path, arcname=snap_part_conf["LibName"])
            with tempfile.NamedTemporaryFile(mode="w") as cmake_file:
                cmake_file.write(cmake_lists_txt)
                cmake_file.flush()
                tfp.add(cmake_file.name, arcname="CMakeLists.txt")
            tfp.add("md.json", arcname="md.json")
        self.logger.info("Done building snap part lib.")
        return self

    def make_snap_part_headers(self, snap_part_conf):
        self.logger.info("Building snap part header.")
        if not "HeadersSource" in snap_part_conf:
            raise PackageException("Expecting 'LibName' to be present in snap part conf.")
        if not "Name" in snap_part_conf:
            raise PackageException("Expecting 'Name' to be present in snap part conf.")
        cmake_lists_txt = Package.make_cmake_lists_for_snap_part(snap_part_conf)
        self.logger.info("Snap headers CMakeLists.txt: ")
        self.logger.info(cmake_lists_txt)
        with tarfile.open(os.path.join(self.conf["BuildFolder"], snap_part_conf["Name"] + ".tar"), "w") as tfp:
            with tempfile.NamedTemporaryFile(mode="w") as cmake_file:
                cmake_file.write(cmake_lists_txt)
                cmake_file.flush()
                tfp.add(cmake_file.name, arcname="CMakeLists.txt")
            tfp.add(os.path.join(self.conf["ProjectDir"], snap_part_conf["HeadersSource"]),
                    arcname=snap_part_conf["HeadersDest"])
            tfp.add("md.json", arcname="md.json")
        self.logger.info("Done building snap part headers.")
        return self

    def build_all(self):
        for package in self.md["Packaging"]:
            if package["Type"] == "snap":
                self.make_snap(package)
            elif package["Type"] == "snap-part":
                if package["PartType"] == "lib":
                    self.make_snap_part_lib(package)
                else:
                    self.make_snap_part_headers(package)

    @staticmethod
    def getopts(cmd_line_args, config):
        parser = argparse.ArgumentParser(prog="Package", description=__doc__, usage="Package [options]",
                                         formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument("-s", "--snaponly", help="Just package the snap.",
                            action="store_true")
        parser.add_argument("-r", "--headeronly", help="Just package the snap header parts.",
                            action="store_true")
        parser.add_argument("-l", "--libonly", help="Just package the snap lib parts.", action="store_true")
        args = parser.parse_args(cmd_line_args)

        package_config = {
            "LocalPackageCache": os.path.join(os.getcwd(), ".packagecache"),
            "ProjectDir": os.getcwd(),
            "BuildFolder": os.path.join(os.getcwd(), "build")
        }
        config.add_conf_params(package_config)
        package = Package(config.conf, config.logger)

        try:
            if args.snaponly:
                for packaging in config.conf["Packaging"]:
                    if packaging["Type"] == "snap":
                        package.make_snap(packaging)
                return

            if args.headeronly:
                for packaging in config.conf["Packaging"]:
                    if packaging["Type"] == "snap-part" and packaging["PartType"] == "headers":
                        package.make_snap_part_headers(packaging)
                return

            if args.libonly:
                for packaging in config.conf["Packaging"]:
                    if packaging["Type"] == "snap-part" and packaging["PartType"] == "lib":
                        package.make_snap_part_lib(packaging)
                return

            package.build_all()
        except Exception as e:
            config.logger.error(str(e))
            config.logger.error("\nStacktrace:\n--------------------------------------")
            config.logger.error(traceback.format_exc())
            config.logger.error("--------------------------------------\n\n")
            sys.exit(1)
