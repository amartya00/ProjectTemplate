"""
This class contains tools to create resources for a project.
"""

import os
import sys
import re

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")
from libs.Utils import Utils


class CreateResources (object):
    def __init__(self, templatemap, jsonobj, projroot):
        self.templatemap = templatemap
        self.jsonobj = jsonobj
        self.projroot = projroot

    def replace_str(self, value):
        sobj = re.match(".*<(.*)>.*", value.strip())
        if sobj and sobj.group(1) in self.templatemap.keys():
            newstr = value.strip().replace(sobj.group(1), self.templatemap[sobj.group(1)]).replace("<","").replace(">","")
            return newstr
        else:
            return None

    def apply_templates_to_property(self, projectdict):
        if type(projectdict) == list:
            for i in range(0, len(projectdict)):
                if type(projectdict[i]) == str:
                    retval = self.replace_str(projectdict[i])
                    if retval:
                        projectdict[i] = retval
                else:
                    projectdict[i] = self.apply_templates_to_property(projectdict[i])
        elif type(projectdict) == dict:
            for k in projectdict.keys():
                if type(projectdict[k]) == str or type(projectdict[k]) == unicode:
                    retval = self.replace_str(projectdict[k])
                    if retval:
                        projectdict[k] = retval
                else:
                    projectdict[k] = self.apply_templates_to_property(projectdict[k])
        return projectdict

    def create_resources_recursively(self, root, projectdict):
        if projectdict["Type"] == "Directory":
            if os.path.isdir(os.path.join(root, projectdict["Name"])):
                Utils.warn("Folder " + os.path.join(root, projectdict["Name"]) + " already exists. Skipping")
            else:
                Utils.info("Creating folder: " + os.path.join(root, projectdict["Name"]))
                os.makedirs(os.path.join(root, projectdict["Name"]))
            for k in projectdict["Contents"]:
                self.create_resources_recursively(os.path.join(root, projectdict["Name"]), k)
        elif projectdict["Type"] == "File":
            if os.path.isfile(os.path.join(root, projectdict["Name"])):
                Utils.warn("File " + os.path.join(root, projectdict["Name"]) + " already exists. Skipping")
            else:
                Utils.info("Creating file: " + os.path.join(root, projectdict["Name"]))
                fp = open(os.path.join(root, projectdict["Name"]), "w")
                fp.write(projectdict["Contents"])
                fp.close()

    def run(self):
        self.jsonobj = self.apply_templates_to_property(self.jsonobj)
        self.create_resources_recursively(self.projroot, self.jsonobj)