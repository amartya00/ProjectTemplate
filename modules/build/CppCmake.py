"""
This module is responsible for building c++ code using CMake.
Required config parameters are:
1. Package cache
2. Build folder
3. Logger
"""
import subprocess
import os
import shutil


class BuildException (Exception):
    pass


class CppCmake:
    @staticmethod
    def cmake(root, build_folder, package_cache, logger):
        try:
            current = os.getcwd()
            os.chdir(build_folder)
            p = subprocess.Popen(["cmake", root, "-DPACKAGE_CACHE=" + package_cache], stdout=subprocess.PIPE)
            o, e = p.communicate()
            logger.info("Running command: cmake " + root + " -DPACKAGE_CACHE=" + package_cache)
            logger.info(o)
            logger.info(e)
            os.chdir(current)
        except OSError as e:
            raise BuildException(str(e))

    @staticmethod
    def make(build_folder, args=[]):
        try:
            current = os.getcwd()
            os.chdir(build_folder)
            p = subprocess.Popen(["make"] + args)
            p.communicate()
            os.chdir(current)
        except OSError as e:
            raise BuildException(str(e))

    def __init__(self, config_obj):
        self.root = os.getcwd()
        self.package_cache = config_obj["LocalPackageCache"]
        self.build_dir = config_obj["BuildDir"]
        self.logger = config_obj["Logger"]

    def build(self):
        if not os.path.isdir(self.build_dir):
            self.logger.info("Creating build dir: " + self.build_dir)
            try:
                os.makedirs(self.build_dir)
            except OSError as e:
                raise BuildException("Could not create build folder because " + str(e))
        CppCmake.cmake(self.root, self.build_dir, self.package_cache, self.logger)
        CppCmake.make(self.build_dir)

    def run_tests(self):
        if not os.path.isdir(self.build_dir):
            self.logger.warn("Could not find build dir. Building first.")
            self.build()
        CppCmake.make(self.build_dir, ["test"])

    def clean(self):
        if os.path.isdir(self.build_dir):
            shutil.rmtree(self.build_dir)

        if os.path.isdir(self.package_cache):
            shutil.rmtree(self.package_cache)
