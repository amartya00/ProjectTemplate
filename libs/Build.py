import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")
from libs.Utils import Utils


class BuilderException (Exception):
    def __init__(self, message = "Unknown exception"):
        self.message = message

    def __str__(self):
        return self.message


class Builder:
    PACKAGE_TYPES = ["snap", "part"]

    def __init__(self, type):
        self.conf = {
            "Bucket": "amartya00-service-artifacts"
        }
        if type not in Builder.PACKAGE_TYPES:
            raise BuilderException("Invalid package type (" + type + "). Availavle types: " + str(Builder.PACKAGE_TYPES))
        self.conf["Type"] = type

    def make_part(self, root, libname):
        Utils.make_package(root, libname, self.conf["Bucket"])

