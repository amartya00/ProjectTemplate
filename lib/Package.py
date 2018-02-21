"""
Class: Package
Configuration parameters needed:
1. LocalPackageCache
2. PackageCacheRoot
3. BucketName
4. ProjectDir
5. BuildFolder
"""

import os
import json
import sys
import tempfile
import subprocess
import shutil

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")
sys.dont_write_bytecode = True

from lib.DependencyResolver import DependencyResolver
from lib.PackageDownloader import PackageDownloader


class PackageException(Exception):
    def __init__(self, message = "Unknown exception"):
        self.message = message

    def __str__(self):
        return self.message


class Package:
    def __init__(self, md, conf, logger):
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

    def get_package_path(self, package_name, package_version):
        tar_folder = os.path.join(self.conf["PackageCacheRoot"], os.path.join(package_name, package_version))
        local_path = os.path.join(tar_folder, package_name + ".tar")
        if os.path.isfile(local_path):
            return local_path
        remote_path = PackageDownloader.get_s3_url(self.conf["BucketName"], package_name, package_version)
        return remote_path

    def snappy_yaml(self):
        if "Packaging" not in self.md:
            raise PackageException("Expecting packaging information to be in metadata.")
        if "Type" not in self.md["Packaging"]:
            raise PackageException("Packaging type information missing")
        if self.md["Packaging"]["Type"] != "snap":
            raise PackageException("This is not a snap. Cannot create snappy.yaml")
        snappy = self.md["Packaging"]
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
        return yamlstr

    def make_snap(self):
        with tempfile.TemporaryDirectory() as temp_folder:
            snap_folder = os.path.join(temp_folder, "snap")
            os.makedirs(snap_folder)
            with open(os.path.join(snap_folder, "snapcraft.yaml"), "w") as fp:
                fp.write(self.snappy_yaml())
                self.logger.info("Created snapcraft.yaml in temporary folder: " + snap_folder)
            cwd = os.getcwd()
            os.chdir(temp_folder)
            p = subprocess.Popen(["snapcraft"])
            o, e = p.communicate()
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