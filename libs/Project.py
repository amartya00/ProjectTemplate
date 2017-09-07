"""
This file contains a project object.
"""

import json
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")
from libs.Utils import Utils
from libs.CreateResources import CreateResources


class ProjectException(Exception):
    def __init__(self, message = "Unknown exception"):
        self.message = message

    def __str__(self):
        return self.message


class Project (object):
    projectfilemap = {
        "cpp": "VanillaCpp.json",
        "thrift": "FBThrift.json",
        "html": "HTML.json"
    }

    conf = {
        "ConfRoot": os.path.join(os.environ["HOME"], ".ProjectTemplate"),
        "ProjectFolder": os.path.join(os.environ["HOME"], "Projects"),
        "ConfFile": os.path.join(os.path.join(os.environ["HOME"], ".ProjectTemplate"), ".config")
    }

    @staticmethod
    def datafilepath(ptype):
        if ptype == None:
            raise ProjectException("Project type required.")
        if not ptype in Project.projectfilemap.keys():
            raise ProjectException(
                "Invalid project type. Allowed types are: " + str(Project.projectfilemap.keys()) + ".")
        return os.path.join(os.path.dirname(os.path.realpath(__file__)) + "/../data", Project.projectfilemap[ptype])

    @staticmethod
    def loadconf():
        if not os.path.isdir(Project.conf["ConfRoot"]):
            Utils.info("First run. Creating folder " + Project.conf["ConfRoot"])
            os.makedirs(Project.conf["ConfRoot"])
        if not os.path.isfile(Project.conf["ConfFile"]):
            fp = open(Project.conf["ConfFile"], "w")
            fp.write(json.dumps(Project.conf, indent=4))
            fp.close()
            Utils.info("Created config file: " + Project.conf["ConfFile"])
            return Project.conf
        return json.loads(open(Project.conf["ConfFile"]).read())

    @staticmethod
    def get_projects():
        retval = []
        conf = Project.loadconf()
        if os.path.isdir(conf["ConfRoot"]):
            for f in os.listdir(conf["ConfRoot"]):
                if os.path.isfile(os.path.join(conf["ConfRoot"], f)) and not f == ".config":
                    retval.append(json.loads(open(os.path.join(conf["ConfRoot"], f)).read()))
        return retval

    @staticmethod
    def show_projects():
        print(json.dumps(Project.get_projects(), indent = 4))
        print("\n")

    def __init__(self, definitionFile, name, root):
        self.conf = {
            "Project": json.loads(open(definitionFile).read()),
            "Name": name,
            "Root": root
        }

    def create(self):
        existing_projects = Project.get_projects()
        for p in existing_projects:
            if p["Name"] == self.conf["Name"]:
                raise ProjectException("Project " + self.conf["Name"] + " already exists. Following is more info about it:\n" + json.dumps(p, indent = 4))
        Utils.info("Creating project: " + self.conf["Name"])
        templatemap = {
            "PROJECT_NAME": self.conf["Name"]
        }
        resources = CreateResources(templatemap, self.conf["Project"]["FileSystemStructure"], self.conf["Root"])
        resources.run()

    def save(self, saveroot):
        Utils.info("Saving project: " + self.conf["Name"])
        fp = open(os.path.join(saveroot, self.conf["Name"] + ".json"), "w")
        fp.write(
            json.dumps(
                {
                    "Name": self.conf["Name"],
                    "Root": self.conf["Root"],
                    "Language": self.conf["Project"]["Language"],
                    "LastModified": time.time()
                },
                indent = 4
            )
        )
        fp.close()

