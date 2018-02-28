import tempfile
import os
import sys
import tarfile

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")
sys.dont_write_bytecode = True

from lib.utils.Utils import *


class SnapPartException (Exception):
    def __init__(self, message="Unknown exception."):
        self.message = message

    def __str__(self):
        return self.message


class SnapPart:
    def __init__(self, snap_part_conf):
        self.conf = snap_part_conf

    @staticmethod
    def make_cmake_lists_for_snap_part(snap_part_conf):
        install_target = snap_part_conf["PartType"]
        cmake_str = "cmake_minimum_required(VERSION 3.0)\n"
        if install_target == "lib":
            if "LibName" not in snap_part_conf:
                raise SnapPartException("A lib part type needs a LibName parameter in packaging information.")
            lib_name = snap_part_conf["LibName"]
            cmake_str = cmake_str + "project(" + lib_name + ")\n"
            cmake_str = cmake_str + "file(GLOB libs ${CMAKE_CURRENT_SOURCE_DIR}/*.so*)\n"
            cmake_str = cmake_str + "install(FILES ${libs} DESTINATION lib)"
        elif install_target == "headers":
            if "HeadersSource" not in snap_part_conf:
                raise SnapPartException("Need a headers folder to create a header based snap-part.")
            folder = snap_part_conf["HeadersSource"]
            cmake_str = cmake_str + "project(" + folder + ")\n"
            cmake_str = cmake_str + "install(DIRECTORY ${" + folder + "} DESTINATION headers USE_SOURCE_PERMISSIONS)"
        return cmake_str

    def make_snap_part(self):
        if not "LibName" in self.conf:
            raise SnapPartException("Expecting 'LibName' to be present in snap part conf.")
        if not "Name" in self.conf:
            raise SnapPartException("Expecting 'Name' to be present in snap part conf.")
        # Create the CmakeLists.txt
        cmake_lists_txt = SnapPart.make_cmake_lists_for_snap_part(self.conf)

        # Find the assoiated library
        if not os.path.isdir(self.conf["BuileFolder"]):
            raise SnapPartException(
                "Could not find build folder while trying to build snap part (lib). Make sure the code is built.")
        lib_path = recursive_file_search(self.conf["BuildFolder"], self.conf["LibName"])
        if not lib_path:
            raise SnapPartException("Could not find library " + self.conf["LibName"] + " in build folder.")
        with tarfile.open(self.conf["Name"] + ".tar", "w") as tfp:
            tfp.add(lib_path, arcname=self.conf["LibName"])
            with tempfile.NamedTemporaryFile() as cmake_file:
                cmake_file.write(cmake_lists_txt)
                cmake_file.flush()
                tfp.add(cmake_file.name, arcname="CmakeLists.txt")
            tfp.add(lib_path, arcname=self.conf["LibName"])
        return self
