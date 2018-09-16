"""
This module installed downloaded packages from the global package cache to the project specific cache.
It assumes that the folders of all the packages passed as arguments exists. If not, it will throw.
It also returns the collective dependencies of all the packages it installed.
"""

import subprocess
import os
import json


class PackageInstallerException (Exception):
    pass


class PackageInstaller:
    @staticmethod
    def cmake(src_folder, dest_folder, logger):
        current = os.getcwd()
        os.chdir(src_folder)
        try:
            p = subprocess.Popen(["cmake", ".", "-DCMAKE_INSTALL_PREFIX=" + dest_folder], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            exit_code = True if p.returncode == 0 else False
        except OSError as e:
            logger.error("Could not run cmake. Please check if cmake is installed on your system. " + str(e))
            os.chdir(current)
            return False
        if not exit_code:
            logger.error(err)
            logger.error("CMAKE command failed with error code " + str(p.returncode) + " !")
        else:
            logger.info(out)
        os.chdir(current)
        return exit_code

    @staticmethod
    def make(src_folder, logger, args=[]):
        current = os.getcwd()
        os.chdir(src_folder)
        try:
            p = subprocess.Popen(["make"] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            exit_code = True if p.returncode == 0 else False
        except OSError as e:
            logger.error("Could not run make. Please make sure make is installed on your system. " + str(e))
            os.chdir(current)
            return False
        os.chdir(current)
        if not exit_code:
            logger.error(err)
            logger.error("MAKE command failed with error code " + str(p.returncode) + " !")
        else:
            logger.info(out)
        return exit_code

    def __init__(self, config_obj):
        try:
            self.local_cache = config_obj["LocalPackageCache"]
            self.global_cache = config_obj["GlobalPackageCache"]
            self.logger = config_obj["Logger"]
        except KeyError as e:
            raise PackageInstallerException("Invalid config object " + str(e))
        except TypeError as e1:
            raise PackageInstallerException(str(e1))

    def install_a_package(self, package_name, package_version):
        package_src = os.path.join(
            self.global_cache,
            package_name,
            package_version
        )
        package_dest = self.local_cache
        if not os.path.isdir(package_src):
            raise PackageInstallerException("The package " + package_name + "/" + package_version + " is not downloaded. Cannot install.")
        if not os.path.isdir(package_dest):
            os.makedirs(package_dest)
        # Cmake
        return_code = PackageInstaller.cmake(package_src, package_dest, self.logger)
        if not return_code:
            raise PackageInstallerException("CMake failed on package " + package_name + "/" + package_version)
        # Make
        return_code = PackageInstaller.make(package_src, self.logger)
        if not return_code:
            raise PackageInstallerException("Make failed on package " + package_name + "/" + package_version)
        # Make install
        return_code = PackageInstaller.make(package_src, self.logger, ["install"])
        if not return_code:
            raise PackageInstallerException("Make install failed on package " + package_name + "/" + package_version)

    def get_package_dependency(self, package_name, package_version):
        md_file = os.path.join(
            self.global_cache,
            package_name,
            package_version,
            "md.json"
        )
        try:
            with open(md_file, "r") as fp:
                md = json.loads(fp.read())
                deps = []
                if "Dependencies" in md:
                    deps.extend(md["Dependencies"])
                if "BuildDeps" in md:
                    deps.extend(md["BuildDeps"])
                if "TestDeps" in md:
                    deps.extend(md["TestDeps"])
                if "RuntimeDeps" in md:
                    deps.extend(md["RuntimeDeps"])
                return deps
        except OSError as e:
            raise PackageInstallerException("Could not read metadata file " + md_file + " because " + str(e) + ".")
        except ValueError as e1:
            raise PackageInstallerException("Could not read metadata file " + md_file + " because " + str(e1) + ".")

    def install_packages(self, package_list):
        dependencies = {}
        for package in package_list:
            package_name = package["Name"]
            package_version = package["Version"]
            self.install_a_package(package_name, package_version)
            for dep in self.get_package_dependency(package_name, package_version):
                dependencies[dep["Name"]] = dep
        return dependencies

