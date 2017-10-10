import os
import sys
import json
import boto3
import botocore
import tarfile
import subprocess
import shutil

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")
from libs.Utils import Utils


class BuilderException (Exception):
    def __init__(self, message = "Unknown exception"):
        self.message = message

    def __str__(self):
        return self.message


class Builder:
    PACKAGE_TYPES = ["snap", "part"]

    conf = {
        "ConfRoot": os.path.join(os.environ["HOME"], ".ProjectTemplate"),
        "ProjectFolder": os.path.join(os.environ["HOME"], "Projects"),
        "ConfFile": os.path.join(os.path.join(os.environ["HOME"], ".ProjectTemplate"), ".config")
    }

    @staticmethod
    def loadconf():
        if not os.path.isdir(Builder.conf["ConfRoot"]):
            Utils.info("First run. Creating folder " + Builder.conf["ConfRoot"])
            os.makedirs(Builder.conf["ConfRoot"])
        if not os.path.isfile(Builder.conf["ConfFile"]):
            fp = open(Builder.conf["ConfFile"], "w")
            fp.write(json.dumps(Builder.conf, indent=4))
            fp.close()
            Utils.info("Created config file: " + Builder.conf["ConfFile"])
            return Builder.conf
        return json.loads(open(Builder.conf["ConfFile"]).read())

    def __init__(self):
        self.conf = {
            "Bucket": "amartya00-service-artifacts",
            "BuildFolder": os.path.join(os.getcwd(), "build"),
        }
        conf = Builder.loadconf()
        if "Bucket" in conf.keys():
            self.conf["Bucket"] = conf["Bucket"]
        if not os.path.isfile(os.path.join(os.getcwd(), "md.json")):
            raise BuilderException("Expect a md.json file in $PWD")
        else:
            try:
                self.conf["MD"] = json.loads(open(os.path.join(os.getcwd(), "md.json")).read())
                self.conf["PackageCache"] = os.path.join(os.getcwd(), ".packagecache")
                self.conf["PackageCacheLibs"] = os.path.join(self.conf["PackageCache"], "lib")
                self.conf["PackageCacheHeaders"] = os.path.join(self.conf["PackageCache"], "headers")
                self.conf["BuildDir"] = os.path.join(os.getcwd(), "build")
                self.conf["ProjectDir"] = os.getcwd()
            except Exception as e:
                raise BuilderException("Could not read md.json file: " + str(e))

        if not os.path.isdir(self.conf["PackageCache"]):
            os.makedirs(self.conf["PackageCache"])
        if not os.path.isdir(self.conf["PackageCacheLibs"]):
            os.makedirs(self.conf["PackageCacheLibs"])
        if not os.path.isdir(self.conf["PackageCacheHeaders"]):
           os.makedirs(self.conf["PackageCacheHeaders"])
        self.s3client = boto3.client("s3")

    def download_package(self, packagename, version):
        key = packagename + "/" + version + "/" + packagename + ".tar"
        packagedir = os.path.join(self.conf["PackageCache"], packagename)
        if os.path.isdir(packagedir):
            shutil.rmtree(packagedir)
            Utils.warn("Folder " + packagedir + " already exists. Overwriting ...")
        try:
            response = self.s3client.get_object(Bucket = self.conf["Bucket"], Key = key)
            fp = open(os.path.join(self.conf["PackageCache"], packagename + ".tar"), "wb")
            fp.write(response["Body"].read())
            fp.close()
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                Utils.warn("Could not find package " + packagename + " in s3 bucket. You need to have in installed locally by some other means.")
            else:
                raise BuilderException(str(e))
        except Exception as e1:
            raise BuilderException("Package cacheing failed: " + str(e1))
        Utils.info("Downloaded package " + packagename + ". Extracting...")
        os.makedirs(packagedir)
        fp = tarfile.open(os.path.join(self.conf["PackageCache"], packagename + ".tar"))
        fp.extractall(path = packagedir)
        fp.close()
        Utils.info("Extracted package " + packagename + " to folder " + packagedir)
        return self

    def install_package(self, packagename):
        packagedir = os.path.join(self.conf["PackageCache"], packagename)
        cwd = os.getcwd()
        os.chdir(packagedir)
        p = subprocess.Popen(["cmake", ".", "-DCMAKE_INSTALL_PREFIX=" + self.conf["PackageCache"]], stdout=subprocess.PIPE)
        o, e = p.communicate()
        Utils.info(str(o))
        Utils.info(str(e))
        p = subprocess.Popen(["make"], stdout=subprocess.PIPE)
        o, e = p.communicate()
        Utils.info(str(o))
        Utils.info(str(e))
        p = subprocess.Popen(["make", "install"], stdout=subprocess.PIPE)
        o, e = p.communicate()
        Utils.info(str(o))
        Utils.info(str(e))
        Utils.info("Downloaded and bootstrapped dependency: " + packagename)
        os.chdir(cwd)
        return self

    def is_package_installed(self, packagename, version, contents):
        if os.path.isdir(self.conf["PackageCache"]):
            if os.path.isdir(os.path.join(self.conf["PackageCache"], packagename)):
                if version == json.loads(open(os.path.join(os.path.join(self.conf["PackageCache"], packagename), "md.json")).read())["Version"]:
                    if ".so" in contents and os.path.isfile(os.path.join(self.conf["PackageCacheLibs"], contents)):
                        return True
        return False

    def resolve_dependencies(self):
        try:
            dependencies = self.conf["MD"]["Dependencies"]
        except Exception as e:
            raise BuilderException("Corrupt md file: " + str(e))
        for d in dependencies:
            Utils.info("Dependency: " + d["Package"])
            if self.is_package_installed(d["Package"], d["Version"], d["Content"]):
                Utils.info("Package " + d["Package"] + " already installed in desired version.")
            else:
                self.download_package(d["Package"], d["Version"]).install_package(d["Package"])
        Utils.info("Dependency resolution complete ...")
        return self

    def run_cmake(self):
        if not os.path.isdir(self.conf["BuildFolder"]):
            os.makedirs(self.conf["BuildFolder"])
        cwd = os.getcwd()
        os.chdir(self.conf["BuildFolder"])
        p = subprocess.Popen(["cmake", self.conf["ProjectDir"], "-DPACKAGE_CACHE=" + self.conf["PackageCache"]], stdout=subprocess.PIPE)
        o, e = p.communicate()
        Utils.info(str(o))
        Utils.info(str(e))
        os.chdir(cwd)
        return self

    def make(self):
        if not os.path.isdir(self.conf["BuildFolder"]):
            raise BuilderException("Build folder not present. Please run the build without the -b option")
        cwd = os.getcwd()
        os.chdir(self.conf["BuildFolder"])
        p = subprocess.Popen(["make"])
        o, e = p.communicate()
        os.chdir(cwd)
        return self

    def run_tests(self):
        cwd = os.getcwd()
        os.chdir(self.conf["BuildFolder"])
        p = subprocess.Popen(["make", "test"], stdout=subprocess.PIPE)
        o, e = p.communicate()
        Utils.info(str(o))
        Utils.info(str(e))
        os.chdir(cwd)
        return self

    def symlink_bootstrapped_libs(self):
        cwd = os.getcwd()
        os.chdir(self.conf["PackageCacheLibs"])
        for l in os.listdir(self.conf["PackageCacheLibs"]):
            if ".so" in l and not l.endswith(".so"):
                Utils.info("Library " + l +" might need to be symlinked.")
                if os.path.isfile(l.split(".")[0] + ".so"):
                    Utils.info("Symlink to " + l + " already exists. Skipping ...")
                else:
                    os.symlink(l, l.split(".")[0] + ".so")
        os.chdir(cwd)
        return self

    def clean(self):
        shutil.rmtree(self.conf["PackageCache"])
        return self

    def make_part(self, root, libname):
        Utils.make_package(root, libname, self.conf["Bucket"])
        return self

    def snappy_yaml(self):
        if "Snappy" not in self.conf["MD"]:
            raise BuilderException("Snappy config not present in md.json. Cannot build a snap.")
        snappy = self.conf["MD"]["Snappy"]
        yamlstr = "name: " + snappy["Name"] + "\n"
        yamlstr = yamlstr + "version: " + "'" + snappy["Version"] + "'\n"
        yamlstr = yamlstr + "summary: " + snappy["Summary"] + "\n"
        yamlstr = yamlstr + "grade: " + snappy["Grade"] + "\n"
        yamlstr = yamlstr + "confinement: " + snappy["Confinement"] + "\n"
        yamlstr = yamlstr + "description: " + snappy["Description"] + "\n\n"
        yamlstr = yamlstr + "apps:\n"
        for a in snappy["Apps"]:
            yamlstr = yamlstr + "  " + a["Name"] + ":\n"
            yamlstr = yamlstr + "    command: " + a["Command"] +"\n\n"

        yamlstr = yamlstr + "parts:\n"
        for d in self.conf["MD"]["Dependencies"]:
            yamlstr = yamlstr + "  " + d["Package"] + ":\n"
            yamlstr = yamlstr + "    plugin: cmake\n"
            if os.path.isfile(os.path.join(self.conf["PackageCache"], d["Package"] + ".tar")):
                yamlstr = yamlstr + "    source: " + os.path.join(self.conf["PackageCache"], d["Package"] + ".tar") + "\n\n"
            else:
                yamlstr = yamlstr + "    source: https://s3.amazonaws.com/" + self.conf["Bucket"] + "/" + d["Package"] + "/" + d["Version"] + "/" + d["Package"] + ".tar\n\n"
        yamlstr = yamlstr + "  " + snappy["Name"] + ":\n"
        yamlstr = yamlstr + "    plugin: cmake\n"
        yamlstr = yamlstr + "    source: " + self.conf["ProjectDir"] + "\n"
        yamlstr = yamlstr + "    configflags: [-DPACKAGE_CACHE=" + self.conf["PackageCache"] + "]\n\n"
        return yamlstr

    def make_snap(self):
        tmpfolder = os.path.join("/tmp/", self.conf["MD"]["Package"])
        snapfolder = os.path.join(tmpfolder, "snap")
        if os.path.isdir(tmpfolder):
            Utils.info("Removing temporary folder: " + tmpfolder)
            shutil.rmtree(tmpfolder)
        Utils.info("Creating folder: " + tmpfolder)
        os.makedirs(tmpfolder)
        os.makedirs(os.path.join(tmpfolder, "snap"))
        fp = open(os.path.join(snapfolder, "snapcraft.yaml"), "w")
        fp.write(self.snappy_yaml())
        fp.close()
        Utils.info("Created dnapcraft.yaml")

        cwd = os.getcwd()
        os.chdir(tmpfolder)
        p = subprocess.Popen(["snapcraft"])
        o, e = p.communicate()
        if not p.returncode == 0:
            Utils.error("Building snap failed.")
        else:
            Utils.info("Built snap in folder: " + tmpfolder)
            for s in os.listdir(tmpfolder):
                if s.endswith(".snap"):
                    shutil.copyfile(os.path.join(tmpfolder, s), os.path.join(self.conf["BuildFolder"], s))
                    Utils.info("Copied the snap to: " + os.path.join(self.conf["BuildFolder"], s))
                    Utils.info("Finshed snap building process.")
        os.chdir(cwd)



