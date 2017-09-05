"""
This contains resources to create a HTML project
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")
from libs.Utils import Utils


class HTMLProject:
    def __init__(self, name, root):
        self.conf = {
            "ProjectName": name,
            "ProjectLang": "cpp",
            "ProjectRoot": root,
            "SubDirs":  ["html", "js"]
        }

    @staticmethod
    def htmlfile():
        retval = ""
        retval = retval + "<!DOCTYPE html>\n"
        retval = retval + "<html>\n"
        retval = retval + "  <meta charset=\"utf-8\">\n"
        retval = retval + "  <head>"
        retval = retval + "    <title></title>\n"
        retval = retval + "    <style type=\"text/css\"></style>"
        retval = retval + "  </head>"
        retval = retval + "  <body>\n</body>"
        retval = retval + "</body>"
        return retval

    @staticmethod
    def gitignore():
        return "build/\n"

    def create_resources(self):
        # Folders
        if not os.path.isdir(self.conf["ProjectRoot"]):
            os.makedirs(self.conf["ProjectRoot"])
            Utils.info("Created folder: " + self.conf["ProjectRoot"])
        for s in self.conf["SubDirs"]:
            if not os.path.isdir(os.path.join(self.conf["ProjectRoot"], s)):
                os.makedirs(os.path.join(self.conf["ProjectRoot"], s))
                Utils.info("Created folder: " + s)

        # Index.html
        if not os.path.isfile(os.path.join(self.conf["ProjectRoot"], "index.html")):
            fp = open(os.path.join(self.conf["ProjectRoot"], "index.html"), "w")
            fp.write(HTMLProject.htmlfile())
            fp.close()
            Utils.info("Created index.html")

        # Gitignore
        if not os.path.isfile(os.path.join(self.conf["ProjectRoot"], ".gitignore")):
            fp = open(os.path.join(self.conf["ProjectRoot"], ".gitignore"), "w")
            fp.write(HTMLProject.gitignore())
            fp.close()
            Utils.info("Created .gitignore file")