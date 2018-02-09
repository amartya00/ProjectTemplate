import os
import sys
import subprocess
import shutil

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")
sys.dont_write_bytecode = True

from lib.DependencyResolver import DependencyResolverException, DependencyResolver


class BuildException (Exception):
    def __init__(self, message = "Unknown exception"):
        self.message = message

    def __str__(self):
        return self.message


class Build:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.packagecache = self.config["LocalPackageCache"]
        self.build_folder = self.config["BuildFolder"]

    def bootstrap(self):
        dependency_resolver = DependencyResolver(config=self.config, logger=self.logger)
        dependency_resolver.bfs()
        return self

    def symlink_bootstrapped_libs(self):
        cwd = os.getcwd()
        os.chdir(self.packagecache)
        for l in os.listdir(self.packagecache):
            if ".so" in l and not l.endswith(".so"):
                self.logger.info("Library " + l + " might need to be symlinked.")
                if os.path.isfile(l.split(".")[0] + ".so"):
                    self.logger.info("Symlink to " + l + " already exists. Skipping ...")
                else:
                    os.symlink(l, l.split(".")[0] + ".so")
        os.chdir(cwd)
        return self

    def run_cmake(self):
        if not os.path.isdir(self.build_folder):
            os.makedirs(self.build_folder)
        cwd = os.getcwd()
        os.chdir(self.build_folder)
        p = subprocess.Popen(["cmake", self.config["ProjectDir"], "-DPACKAGE_CACHE=" + self.packagecache],
                             stdout=subprocess.PIPE)
        o, e = p.communicate()
        self.logger.info(str(o))
        self.logger.info(str(e))
        os.chdir(cwd)
        return self

    def run_make(self):
        if not os.path.isdir(self.build_folder):
            raise BuildException("Build folder not present. Please run the build without the -b option")
        cwd = os.getcwd()
        os.chdir(self.build_folder)
        p = subprocess.Popen(["make"])
        o, e = p.communicate()
        os.chdir(cwd)
        return self

    def run_tests(self):
        cwd = os.getcwd()
        os.chdir(self.build_folder)
        p = subprocess.Popen(["make", "test"], stdout=subprocess.PIPE)
        o, e = p.communicate()
        self.logger.info(str(o))
        self.logger.info(str(e))
        os.chdir(cwd)
        return self

    def clean(self):
        if os.path.isdir(self.packagecache):
            shutil.rmtree(self.packagecache)
            self.logger.info("Cleaned packagecache " + self.packagecache)
        if os.path.isdir(self.build_folder):
            shutil.rmtree(self.build_folder)
            self.logger.info("Cleaned build folder: " + self.build_folder)
        self.logger.info("Done cleaning ...")
        return self