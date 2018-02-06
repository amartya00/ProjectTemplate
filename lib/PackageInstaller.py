import os
import sys
import subprocess
import json

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")
sys.dont_write_bytecode = True


class PackageInstallerException (Exception):
    def __init__(self, message="Unknown exception"):
        self.message = message

    def __str__(self):
        return self.message


class PackageInstaller:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.cwd = os.getcwd()
        self.packagecache = os.path.join(self.cwd, ".packagecache")
        if not os.path.isfile(os.path.join(self.cwd, "md.json")):
            self.logger.error("Expected to find md.json file in CWD. Not there!")
            raise PackageInstallerException("Expected md.json file in $CWD.")
        if not os.path.isdir(self.packagecache):
            self.logger.info("Package cache not present. Creating package cache " + self.packagecache)
            os.makedirs(self.packagecache)

    def install(self, package_name, package_version):
        local_source = os.path.join(
            self.config["PackageCacheRoot"],
            os.path.join(package_name, package_version)
        )
        local_dest = self.packagecache
        os.chdir(local_source)
        # CMAKE
        self.logger.info("Calling cmake in extracted packege: " + package_name + "/" + package_version + ".")
        p = subprocess.Popen(["cmake", ".", "-DCMAKE_INSTALL_PREFIX=" + local_dest], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        exit_code = True if p.returncode == 0 else False
        if not exit_code:
            self.logger.error(str(err))
            self.logger.error("CMAKE command failed with error code " + str(p.returncode) + " !")
            raise PackageInstallerException("CMAKE command exited with code " + str(p.returncode))
        else:
            self.logger.info(str(out))

        # MAKE
        self.logger.info("Calling make.")
        p = subprocess.Popen(["make"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        exit_code = True if p.returncode == 0 else False
        if not exit_code:
            self.logger.error(str(err))
            self.logger.error("MAKE command failed with error code " + str(p.returncode) + " !")
            raise PackageInstallerException("MAKE command exited with code " + str(p.returncode))
        else:
            self.logger.info(str(out))

        # MAKE INSTALL
        self.logger.info("Calling make install.")
        p = subprocess.Popen(["make", "install"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        exit_code = True if p.returncode == 0 else False
        if not exit_code:
            self.logger.error(str(err))
            self.logger.error("MAKE INSTALL command failed with error code " + str(p.returncode) + " !")
            raise PackageInstallerException("MAKE INSTALL command exited with code " + str(p.returncode))
        else:
            self.logger.info(str(out))
        self.logger.info("Successfully installed package " + package_name + "/" + package_version + " to " + local_dest)
        os.chdir(self.cwd)

    def get_installed_md(self, package_name, package_version):
        cache_folder = os.path.join(
            self.config["PackageCacheRoot"],
            os.path.join(package_name, package_version)
        )
        if not os.path.isdir(cache_folder):
            self.logger.error("Packege " + package_name + "/" + package_version + " not installed. Cannot extract metadata.")
            raise PackageInstallerException("Package not installed.")
        md = json.loads(open(os.path.join(cache_folder, "md.json"), "r").read())
        return md



