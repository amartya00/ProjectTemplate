"""
Class: PackageDownloader
Configuration parameters needed:
1. PackageCacheRoot
2. BucketName
"""

import os
import shutil
import sys
import tarfile

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")
sys.dont_write_bytecode = True

from lib.Utils import wget


class PackageDownloaderException(Exception):
    def __init__(self, message="UnknownException"):
        self.message = message

    def __str__(self):
        return self.message


class PackageDownloader:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def prep_folders(self):
        cache_root = self.config["PackageCacheRoot"]
        if not os.path.isdir(cache_root):
            self.logger.info("Creating cache root: " + cache_root)
            os.makedirs(cache_root)

    def download_package(self, package_name, package_version):
        bucket_name = self.config["BucketName"]
        key = package_name + "/" + package_version + "/" + package_name + ".tar"
        url = "https://s3.amazonaws.com/" + bucket_name + "/" + key
        try:
            self.logger.info("Trying to download file: " + key + " from bucket: " + bucket_name)
            cache_folder = os.path.join(
                self.config["PackageCacheRoot"],
                os.path.join(package_name, package_version)
            )
            if not os.path.isdir(cache_folder):
                os.makedirs(cache_folder)
            err, out, exit_code = wget(url, os.path.join(cache_folder, package_name + ".tar"))
            if exit_code:
                self.logger.info(out)
                self.logger.info("Succeeded in downloading package. Proceeding to install.")
            else:
                self.logger.error(err)
                if os.path.isdir(cache_folder):
                    self.logger.warn("Removing folder " + cache_folder)
                    shutil.rmtree(cache_folder)
                raise PackageDownloaderException("Failed to download package")
        except Exception as e:
            self.logger.error(str(e))
            raise PackageDownloaderException(str(e))
        return self

    def extract_package(self, package_name, package_version):
        self.logger.info("Extracting file " + package_name + ".tar")
        cache_folder = os.path.join(
            self.config["PackageCacheRoot"],
            os.path.join(package_name, package_version)
        )
        artifact = os.path.join(cache_folder, package_name + ".tar")
        tfp = tarfile.open(artifact)
        tfp.extractall(path=cache_folder)
        tfp.close()
        self.logger.info("Extracted file " + package_name + ".tar to " + cache_folder)
        return self

    def get_package(self, package_name, package_version):
        if not os.path.isdir(os.path.join(self.config["PackageCacheRoot"],
                                          os.path.join(package_name, package_version)
                                          )
                             ):
            self.logger.info(
                "Package " + package_name + "/" + package_version + " not present locally. Need to download.")
            self.download_package(package_name, package_version).extract_package(package_name, package_version)
        else:
            self.logger.info(
                "Package " + package_name + "/" + package_version + " present locally. No need to download.")
        return self

    def clear_cache(self, package_list):
        for package_name, package_version in package_list:
            self.logger.info("Clearing " + package_name + "/" + package_version)
            cache_folder = os.path.join(
                self.config["PackageCacheRoot"],
                os.path.join(package_name, package_version)
            )
            try:
                shutil.rmtree(cache_folder)
            except OSError:
                self.logger.warn("Package " + package_name + "/" + package_version + " not found locally. Skipping.")
        self.logger.info("Done clearing cache.")
        return self
