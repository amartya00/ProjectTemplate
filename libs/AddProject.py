"""
This utility helps add an existing project.
Valid project types:
* cpp
* thrift
* html
"""

import os
import sys
import argparse

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")
from libs.Project import Project, ProjectException


def getopts(cmdlineargs):
    parser = argparse.ArgumentParser(prog="AddProject", description=__doc__, usage="Todo [options]",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-t", "--type", help="The typr of project you want to create. Available types: " + str(Project.projectfilemap.keys()))
    parser.add_argument("-n", "--name", help="Name of the project.")
    parser.add_argument("-r", "--root", help="Location of the project.")
    parser.add_argument("-f", "--templatefile", help="A custom project template if you want.")
    args = parser.parse_args(cmdlineargs)

    name = None
    type = None
    root = None
    templatefile = None

    if args.name:
        name = args.name
    else:
        raise ProjectException("Project name required.")

    if args.type:
        type = args.type

    if args.root:
        root = args.root
    else:
        root = Project.loadconf()["ProjectFolder"]

    if args.templatefile:
        templatefile = args.templatefile
    else:
        templatefile = Project.datafilepath(type)

    p = Project(templatefile, name, root)
    p.add(Project.loadconf()["ConfRoot"])

    return True
