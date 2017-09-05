"""
File that contains the necessary template to create a c++ project.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")
from libs.Utils import Utils


class CPPProject (object):
    def __init__(self, name, root):
        self.conf = {
            "ProjectName": name,
            "ProjectLang": "cpp",
            "ProjectRoot": root,
            "SubDirs":  ["src", "libs", "headers"]
        }

    @staticmethod
    def cmakelistsfile(src):
        retval = "# CMakeLists file for subdir: " + src + "\n"
        retval = retval + "cmake_minimum_required(VERSION 3.0)\n"
        return retval

    @staticmethod
    def gitignore():
        return "build/\nCMakeLists.txt.user\n"

    def create_resources(self):
        # Folders
        if not os.path.isdir(self.conf["ProjectRoot"]):
            os.makedirs(self.conf["ProjectRoot"])
            Utils.info("Created folder: " + self.conf["ProjectRoot"])
        for s in self.conf["SubDirs"]:
            if not os.path.isdir(os.path.join(self.conf["ProjectRoot"], s)):
                os.makedirs(os.path.join(self.conf["ProjectRoot"], s))
            Utils.info("Created folder: " + s)

        # Cmake files
        if not os.path.isfile(os.path.join(self.conf["ProjectRoot"], "CMakeLists.txt")):
            fp = open(os.path.join(self.conf["ProjectRoot"], "CMakeLists.txt"), "w")
            fp.write(CPPProject.cmakelistsfile(self.conf["ProjectRoot"]))
            fp.close()
            Utils.info("Created CMAkeLists.txt in folder: " + self.conf["ProjectRoot"])
        for s in self.conf["SubDirs"]:
            dirpath = os.path.join(self.conf["ProjectRoot"], s)
            if not os.path.isfile(os.path.join(dirpath, "CMakeLists.txt")):
                fp = open(os.path.join(dirpath, "CMakeLists.txt"), "w")
                fp.write(CPPProject.cmakelistsfile(s))
                fp.close()
                Utils.info("Created CMAkeLists.txt in folder: " + s)

        # Gitignore
        if not os.path.isfile(os.path.join(self.conf["ProjectRoot"], ".gitignore")):
            fp = open(os.path.join(self.conf["ProjectRoot"], ".gitignore"), "w")
            fp.write(CPPProject.gitignore())
            fp.close()
            Utils.info("Created .gitignore file")

