"""
Utility to make a snap part / snap from a CXX library
"""

import os
import sys
import argparse

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")
from libs.Build import Builder, BuilderException


def getopts(cmdlineargs):
    parser = argparse.ArgumentParser(prog="MakePackage", description=__doc__, usage="MakePackage [options]",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-t", "--type", help="Type of package you want to build. Available types: " + str(Builder.PACKAGE_TYPES))
    parser.add_argument("-n", "--name", help="Name of the library.")
    parser.add_argument("-r", "--root", help="Location of the library.")
    args = parser.parse_args(cmdlineargs)

    name = None
    type = None
    root = None

    if args.name:
        name = args.name

    if args.type:
        type = args.type
    else:
        raise BuilderException("Package type required. Available types: " + str(Builder.PACKAGE_TYPES))

    if type == "part":
        if name == None:
            raise BuilderException("Library name is needed while trying to make a snap part.")
        b = Builder()
        b.make_part(root, name)
    else:
        b = Builder()
        print(b.make_snap())

    return True


