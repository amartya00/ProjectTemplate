"""
This module is responsible for downloading a bunch of packages and extracting them.
The config object needs to have a section specifying package source information. The information
should contain the package source type (url or s3). Depending on source type, further information is needed.

The package which is assumed to be a tar file is downloaded and saved in <global_package_cache>/package_name/package_version/package_name.tar file.
Note that each package can have its individual source override. So you can download packages from different locations.

After downloading, it is extracted inside the same folder.

Config parameters needed:
1. GlobalPackageCache
2. PackageSource
3. Logger

Initialization parameters:
A list of packages where each member of the list is of the form:
{
    "Name": "MyPackageName",
    "Version": "1.0",
    "PackageSource": {  # OPTIONAL
        "Type": "URL",
        "URL": "https://my_ftp_server/sub_folder"
    }
}

OR

{
    "Name": "MyPackageName",
    "Version": "1.0",
    "PackageSource": {  # OPTIONAL
        "Type": "S3",
        "Bucket": "MyS3Bucket"
    }
}
"""
import subprocess
import os
import boto3
import tarfile

from botocore.exceptions import ClientError


class PackageDownloaderException (Exception):
    pass


class PackageDownloader:
    @staticmethod
    def wget(url, dest):
        try:
            p = subprocess.Popen(["wget", url, "-O", dest], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            err, out = p.communicate()
            exit_code = True
            if "ERROR" in str(out) or p.returncode != 0:
                err = out
                out = ""
                exit_code = False
            return err, out, exit_code
        except OSError as e:
            err = str(e)
            out = ""
            exit_code = False
            return err, out, exit_code

    def __init__(self, config_object):
        try:
            self.global_package_cache = config_object["GlobalPackageCache"]
            self.global_package_info = config_object["PackageSource"]
            self.logger = config_object["Logger"]
            self.s3_client = boto3.client("s3")
        except KeyError as e1:
            raise PackageDownloaderException(str(e1))
        except TypeError as e2:
            raise PackageDownloaderException(str(e2))

    def prep_cache(self):
        if not os.path.isdir(self.global_package_cache):
            self.logger.info("Creating global package cache.")
            os.makedirs(self.global_package_cache)
        self.logger.info("Done setting up global cache.")
        return self

    def download_a_package_if_needed(self, package_name, package_version, source_info):
        try:
            self.prep_cache()
            source_type = source_info["Type"]
            dest_folder = os.path.join(self.global_package_cache, package_name, str(package_version))
            dest = os.path.join(dest_folder, package_name + ".tar")
            if os.path.isfile(dest):
                self.logger.info("Package " + package_name + "/" + str(package_version ) + " already downloaded. Skipping.")
                return self
            else:
                if not os.path.isdir(dest_folder):
                    os.makedirs(dest_folder)
            self.logger.info("Downloading package " + package_name + " : " + str(package_version) + " of type " + source_type)
            if source_type.lower() == "url":
                url = source_info["Url"] + "/" + package_name + "/" + str(package_version) + "/" + package_name + ".tar"
                err, out, exit_code = PackageDownloader.wget(url, dest)
                if not exit_code:
                    raise PackageDownloaderException("Failed to download package " + url + ".")
                self.logger.info(out)
                self.logger.info(err)
                self.logger.info("Downloaded " + url + ".")
            elif source_type.lower() == "s3":
                bucket = source_info["Bucket"]
                key = package_name + "/" + str(package_version) + "/" + package_name + ".tar"
                with open(dest, "w") as fp:
                    try:
                        self.s3_client.download_fileobj(bucket, key, fp)
                    except ClientError as e:
                        raise PackageDownloaderException(e.response["Error"]["Code"])
                self.logger.info("Downloaded package " + package_name + "/" + str(package_version) + " from S3 bucket " + bucket + ".")
        except KeyError as ex:
            raise PackageDownloaderException("Malformed package info " + str(ex))
        except TypeError as ex1:
            raise PackageDownloaderException("Malformed package info " + str(ex1))
        except OSError as ex2:
            raise PackageDownloaderException(str(ex2))
        return self

    def extract_one_package(self, package_name, package_version):
        try:
            downloaded_file = os.path.join(self.global_package_cache, package_name, str(package_version), package_name + ".tar")
            extract_path = os.path.join(self.global_package_cache, package_name, str(package_version))
            tfp = tarfile.open(downloaded_file)
            tfp.extractall(path=extract_path)
            tfp.close()
            self.logger.info("Extracted file " + downloaded_file + ".")
        except OSError as e:
            raise PackageDownloaderException(str(e))
        return self

    def download_and_extract(self, package_list):
        for package in package_list:
            package_name = package["Name"]
            package_version = package["Version"]
            if "PackageSource" not in package:
                package_source_info = self.global_package_info
            else:
                package_source_info = package["PackageSource"]
            self.download_a_package_if_needed(package_name, package_version, package_source_info).extract_one_package(package_name, package_version)
