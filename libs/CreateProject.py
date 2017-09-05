"""
This utility helps create a project.
Valid project types:
* cpp
* thrift
* html
"""

import os
import sys
import json
import argparse

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")
from Utils import Utils
from libs.Cpp import CPPProject
from libs.FBThrift import FBThriftProject
from libs.HTML import HTMLProject


class CreateProjectException (Exception):
    def __init__(self, message = "Unknown exception"):
        self.message = message

    def __str__(self):
        return "[ERROR] " + self.message


class CreateProject:
    valid_types = ["cpp", "thrift", "html"]
    conf = {
        "ConfRoot": os.path.join(os.environ["HOME"], ".ProjectTemplate"),
        "ProjectFolder": os.path.join(os.environ["HOME"], "Projects"),
        "ConfFile": os.path.join(os.path.join(os.environ["HOME"], ".ProjectTemplate"), ".config")
    }

    @staticmethod
    def loadconf():
        if not os.path.isdir(CreateProject.conf["ConfRoot"]):
            Utils.info("First run. Creating folder " + CreateProject.conf["ConfRoot"])
            os.makedirs(CreateProject.conf["ConfRoot"])
        if not os.path.isfile(CreateProject.conf["ConfFile"]):
            fp = open(CreateProject.conf["ConfFile"], "w")
            fp.write(json.dumps(CreateProject.conf, indent = 4))
            fp.close()
            Utils.info("Created config file: " + CreateProject.conf["ConfFile"])
            return CreateProject.conf
        return json.loads(open(CreateProject.conf["ConfFile"]).read())

    def __init__(self, type, name, root = None):
        self.conf = CreateProject.loadconf()
        self.conf["Name"] = name
        if not root == None:
            self.conf["ProjectFolder"] = root
        if type == "cpp":
            self.conf["Type"] = "cpp"
        elif type == "thrift":
            self.conf["Type"] = "thrift"
        elif type == "html":
            self.conf["Type"] = "html"
        else:
            raise CreateProjectException("Invalid project type: " + type + ". Valid types are: " + str(CreateProject.valid_types))

    def create_project(self):
            name = self.conf["Name"]
            Utils.info("Creating " + self.conf["Type"] + " project with name: " + name)
            cpp = None
            if self.conf["Type"] == "cpp":
                cpp = CPPProject(name, os.path.join(self.conf["ProjectFolder"], name))
            elif self.conf["Type"] == "thrift":
                cpp = FBThriftProject(name, os.path.join(self.conf["ProjectFolder"], name))
            elif self.conf["Type"] == "html":
                cpp = HTMLProject(name, os.path.join(self.conf["ProjectFolder"], name))
            cpp.create_resources()

    @staticmethod
    def getopts(cmdlineargs):
        parser = argparse.ArgumentParser(prog="CreateProject", description=__doc__, usage="Todo [options]",
                                         formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument("-t", "--type", help = "The typr of project you want to create. Available types: " + str(CreateProject.valid_types) + ".")
        parser.add_argument("-n", "--name", help = "Name of the project.")
        parser.add_argument("-r", "--root", help="Location of the project.")
        args = parser.parse_args(cmdlineargs)
        name = None
        type = None
        root = None

        if args.name:
            name = args.name
        if args.type:
            type = args.type
        if args.root:
            root = args.root
        if name == None or type == None:
            raise CreateProjectException("Both name and type required.\n" + parser.print_help())
        proj = CreateProject(type, name, root)
        proj.create_project()
        return True
