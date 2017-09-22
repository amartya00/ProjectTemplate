"""
Bunch of utility functions
"""

import os
import shutil
import boto3
import re
import tarfile
import subprocess

class Utils:
    @staticmethod
    def debug(message):
        if "DEBUG_MODE" in os.environ.keys() and os.environ["DEBUG_MODE"] == "true":
            print("[DEBUG] " + message)

    @staticmethod
    def info(message):
        print("[INFO] " + message)

    @staticmethod
    def error(message):
        print("[ERROR] " + message)

    @staticmethod
    def warn(message):
        print("[WARNING] " + message)

    @staticmethod
    def make_package(root, libname):
        s3client = boto3.client("s3")
        lib_basename = libname.split(".")[0]
        packagename = lib_basename.replace("lib", "")
        packagedir = os.path.join(root, packagename)
        cmakestr = "cmake_minimum_required(VERSION 3.0)\n"
        cmakestr = cmakestr + "project(" + lib_basename + ")\n"
        cmakestr = cmakestr + "file(GLOB libs ${CMAKE_CURRENT_SOURCE_DIR}/*.so*)\n"
        cmakestr = cmakestr + "install(FILES ${libs} DESTINATION lib)"
        print("[INFO] Creating directory " + packagedir)
        os.makedirs(packagedir)

        print("[INFO] Creating CMakeLists.txt for project " + packagename)
        fp = open(os.path.join(packagedir, "CMakeLists.txt"), "w")
        fp.write(cmakestr)
        fp.close()

        print("[INFO] Copying over " + libname)
        shutil.copyfile(os.path.join(root, libname), os.path.join(packagedir, libname))

        print("[INFO] Creating tar " + packagename + ".tar")
        tfp = tarfile.open(packagename + ".tar", "w")
        tfp.add(os.path.join(packagedir, libname), arcname=libname)
        tfp.add(os.path.join(packagedir, "CMakeLists.txt"), arcname="CMakeLists.txt")
        tfp.close()

        print("[INFO] Removing folder " + packagedir)
        shutil.rmtree(packagedir)

        print("[INFO] Uploading " + packagename + ".tar to s3 bucket amartya00-service-artifacts")
        s3client.put_object(ACL="public-read", Bucket="amartya00-service-artifacts", Key=packagename + ".tar",
                            Body=open(packagename + ".tar", "rb").read())

    @staticmethod
    def list_libs(root):
        allfiles = os.listdir(root)
        alllibs = []
        for f in allfiles:
            if re.match("lib(.*).so(.*)", f):
                alllibs.append(f)
        return alllibs

    @staticmethod
    def build_packages(root):
        libs = Utils.list_libs(root)
        for l in libs:
            Utils.make_package(root, l)

    @staticmethod
    def ldd(libpath):
        libs = []
        p = subprocess.Popen(["ldd", libpath], stdout=subprocess.PIPE)
        o, e = p.communicate()
        for l in o.split("\n"):
            if l.strip() == "":
                continue
            else:
                temp = l.split("=>")
                if "vdso" in temp[0].strip():
                    continue
                elif temp[0].strip().lower() == "statically linked":
                    continue
                elif len(temp) == 2:
                    libs.append((temp[0].split(" ")[0].strip(), temp[1].strip().split(" ")[0]))
                else:
                    libs.append((temp[0].split("/")[-1].split(" ")[0].strip(), temp[0].split(" ")[0].strip()))
        return libs

    @staticmethod
    def recursively_gather_libs(input_dict, library):
        deps = Utils.ldd(library)
        for d in deps:
            if d[0] not in input_dict.keys():
                print("[INFO] Gathering dependencies for: " + d[0])
                input_dict[d[0]] = d[1]
                Utils.recursively_gather_libs(input_dict, d[1])

    @staticmethod
    def resolve_dependencies(libname):
        results = dict()
        Utils.recursively_gather_libs(results, libname)
        return results
