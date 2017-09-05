"""
FBThrift project template.
This is a vanilla c++ template + the thrift folder
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")
from libs.Cpp import CPPProject
from Utils import Utils


class FBThriftProject (CPPProject):
    def __init__(self, name, root):
        super(FBThriftProject, self).__init__(name, root)

    def create_resources(self):
        super(FBThriftProject, self).create_resources()
        thriftdir = os.path.join(self.conf["ProjectRoot"], "thrift")
        if not os.path.isdir(thriftdir):
            os.makedirs(thriftdir)
            Utils.info("Created folder: " + thriftdir)
        if not os.path.isfile(os.path.join(thriftdir, "CMakeLists.txt")):
            fp = open(os.path.join(thriftdir, "CMakeLists.txt"), "w")
            fp.write(CPPProject.cmakelistsfile(thriftdir))
            fp.close()
            Utils.info("Created CMAkeLists.txt in folder: " + thriftdir)
