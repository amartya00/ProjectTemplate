import unittest
import copy
import json
import os

from tst.testutils.Mocks import MockLog, MockTemporaryFilePointer, MockTarfilePointer
from unittest.mock import patch
from modules.package.SnapPart import SnapPartException, SnapPart


class TestSnapPart (unittest.TestCase):
    def setUp(self):
        self.conf = {
            "Name": "TEST_PROJECT",
            "Version": "1.0",
            "ProjectRoot": "ROOT",
            "BuildFolder": "BUILD",
            "Logger": MockLog(),
            "Dependencies": [{"Name": "A", "Version": "1.0"}],
            "RuntimeDeps": [],
            "BuildDeps": [],
            "TestDeps": []
        }

    @patch("tarfile.open", autospec=True)
    @patch("tempfile.NamedTemporaryFile", autospec=True)
    @patch("os.path.isdir", autospec=True)
    @patch("os.listdir", autospec=True)
    def test_headers_happy_case(self, mock_listdir, mock_isdir, mock_tmpfile, mock_tarfile):
        conf = copy.deepcopy(self.conf)
        conf["PartType"] = "headers"
        conf["HeadersSource"] = "HEADERS_SRC"
        conf["HeadersDest"] = "HEADERS_DEST"

        mock_listdir.side_effect = [
            ["MY_PROJECT_F1", "MY_PROJECT_F2", "CMakeLists.txt"],
            [conf["HeadersSource"]]
        ]

        mock_isdir.side_effect = [
            True, # MY_PROJECT_F1
            True # headers
        ]

        cmake_tmpfile = MockTemporaryFilePointer("TEMP_CMAKE")
        md_tmpfile = MockTemporaryFilePointer("TEMP_MD")
        mock_tmpfile.side_effect = [cmake_tmpfile, md_tmpfile]

        tfp = MockTarfilePointer()
        mock_tarfile.side_effect = [tfp]

        part_builder = SnapPart(conf)
        part_builder.generate_snap_part()

        expected_cmake_str = "cmake_minimum_required(VERSION 3.0)\n" + \
            "project(TEST_PROJECT)\ninstall(DIRECTORY " + conf["HeadersDest"] + \
            " DESTINATION headers USE_SOURCE_PERMISSIONS)"
        self.assertEqual(expected_cmake_str, cmake_tmpfile.invocations["write"][0])

        expected_md_str = json.dumps({"Dependencies": [{"Name": "A", "Version": "1.0"}]}, indent=4)
        self.assertEqual(expected_md_str, md_tmpfile.invocations["write"][0])

        actual_cmake_fname, actual_cmake_arcname = tfp.invocations["add"][0]
        self.assertEqual("TEMP_CMAKE", actual_cmake_fname)
        self.assertEqual("CMakeLists.txt", actual_cmake_arcname)

        actual_md_fname, actual_md_arcname = tfp.invocations["add"][1]
        self.assertEqual("TEMP_MD", actual_md_fname)
        self.assertEqual("md.json", actual_md_arcname)

        actual_headers_src, actual_headers_dest = tfp.invocations["add"][2]
        self.assertEqual(os.path.join(conf["ProjectRoot"], "MY_PROJECT_F1", conf["HeadersSource"]), actual_headers_src)
        self.assertEqual(conf["HeadersDest"], actual_headers_dest)

    @patch("tarfile.open", autospec=True)
    @patch("tempfile.NamedTemporaryFile", autospec=True)
    @patch("os.path.isdir", autospec=True)
    @patch("os.listdir", autospec=True)
    def test_libs_happy_case(self, mock_listdir, mock_isdir, mock_tmpfile, mock_tarfile):
        conf = copy.deepcopy(self.conf)
        conf["PartType"] = "lib"
        conf["LibNames"] = ["lib1.jar", "lib2.jar"]

        mock_listdir.side_effect = [
            ["jars"],
            conf["LibNames"]
        ]

        mock_isdir.side_effect = [
            True, # Build folder
            True,  # MY_PROJECT_F1
            False, # lib1.jar
            False # lib2.jar
        ]

        cmake_tmpfile = MockTemporaryFilePointer("TEMP_CMAKE")
        md_tmpfile = MockTemporaryFilePointer("TEMP_MD")
        mock_tmpfile.side_effect = [cmake_tmpfile, md_tmpfile]

        tfp = MockTarfilePointer()
        mock_tarfile.side_effect = [tfp]

        part_builder = SnapPart(conf)
        part_builder.generate_snap_part()

        expected_cmake_str = "cmake_minimum_required(VERSION 3.0)\n" + \
            "project(TEST_PROJECT)\n" + \
            "file(GLOB libs ${CMAKE_CURRENT_SOURCE_DIR}/lib1.jar)\n" + \
            "file(GLOB libs ${CMAKE_CURRENT_SOURCE_DIR}/lib2.jar)\n" + \
            "install(FILES ${libs} DESTINATION lib)"
        self.assertEqual(expected_cmake_str, cmake_tmpfile.invocations["write"][0])

        expected_md_str = json.dumps({"Dependencies": [{"Name": "A", "Version": "1.0"}]}, indent=4)
        self.assertEqual(expected_md_str, md_tmpfile.invocations["write"][0])

        actual_cmake_fname, actual_cmake_arcname = tfp.invocations["add"][0]
        self.assertEqual("TEMP_CMAKE", actual_cmake_fname)
        self.assertEqual("CMakeLists.txt", actual_cmake_arcname)

        actual_md_fname, actual_md_arcname = tfp.invocations["add"][1]
        self.assertEqual("TEMP_MD", actual_md_fname)
        self.assertEqual("md.json", actual_md_arcname)

        actual_lib_src, actual_lib_dest = tfp.invocations["add"][2]
        self.assertEqual(os.path.join(conf["BuildFolder"], "jars", "lib1.jar"), actual_lib_src)
        self.assertEqual("lib1.jar", actual_lib_dest)

        actual_lib_src, actual_lib_dest = tfp.invocations["add"][3]
        self.assertEqual(os.path.join(conf["BuildFolder"], "jars", "lib2.jar"), actual_lib_src)
        self.assertEqual("lib2.jar", actual_lib_dest)

    def test_exception_on_missing_part_type(self):
        conf = copy.deepcopy(self.conf)
        conf["LibNames"] = ["lib1.jar", "lib2.jar"]

        snap_part = SnapPart(conf)
        self.assertRaises(SnapPartException, snap_part.generate_snap_part)

    def test_exception_on_missing_lib_names(self):
        conf = copy.deepcopy(self.conf)
        conf["PartType"] = "lib"

        snap_part = SnapPart(conf)
        self.assertRaises(SnapPartException, snap_part.generate_snap_part)

    @patch("os.path.isdir", autospec=True)
    @patch("os.listdir", autospec=True)
    def test_exception_on_missing_libs(self, mock_listdir, mock_isdir):
        conf = copy.deepcopy(self.conf)
        conf["PartType"] = "lib"
        conf["LibNames"] = ["lib1.jar", "lib2.jar"]

        mock_listdir.side_effect = [
            ["jars"],
            ["lib1.jar"]
        ]

        mock_isdir.side_effect = [
            True,  # MY_PROJECT_F1
            False,  # lib1.jar
            False  # lib2.jar
        ]

        snap_part = SnapPart(conf)
        self.assertRaises(SnapPartException, snap_part.generate_snap_part)

    @patch("os.path.isdir", autospec=True)
    @patch("os.listdir", autospec=True)
    def test_exception_on_failure_to_read_libs(self, mock_listdir, mock_isdir):
        conf = copy.deepcopy(self.conf)
        conf["PartType"] = "lib"
        conf["LibNames"] = ["lib1.jar", "lib2.jar"]

        mock_listdir.side_effect = [
            ["jars"],
            OSError()
        ]

        mock_isdir.side_effect = [
            True,  # MY_PROJECT_F1
            False,  # lib1.jar
            False  # lib2.jar
        ]

        snap_part = SnapPart(conf)
        self.assertRaises(SnapPartException, snap_part.generate_snap_part)

    @patch("os.path.isdir", autospec=True)
    @patch("os.listdir", autospec=True)
    def test_exception_on_missing_header_src_folder(self, mock_listdir, mock_isdir):
        conf = copy.deepcopy(self.conf)
        conf["PartType"] = "headers"
        conf["HeadersSource"] = "headers"

        mock_listdir.side_effect = [
            ["src"],
            []
        ]

        mock_isdir.side_effect = [
            True  # src
        ]

        snap_part = SnapPart(conf)
        self.assertRaises(SnapPartException, snap_part.generate_snap_part)

    def test_exception_on_missing_header_src(self):
        conf = copy.deepcopy(self.conf)
        conf["PartType"] = "headers"
        conf["HeadersDest"] = "DEST"

        snap_part = SnapPart(conf)
        self.assertRaises(SnapPartException, snap_part.generate_snap_part)

    def test_exception_on_missing_headers_dest(self):
        conf = copy.deepcopy(self.conf)
        conf["PartType"] = "headers"
        conf["HeadersSource"] = "headers"

        snap_part = SnapPart(conf)
        self.assertRaises(SnapPartException, snap_part.generate_snap_part)

    @patch("os.path.isdir", autospec=True)
    @patch("os.listdir", autospec=True)
    def test_exception_on_missing_build_folder(self, mock_listdir, mock_isdir):
        conf = copy.deepcopy(self.conf)
        conf["PartType"] = "lib"
        conf["LibNames"] = ["lib1.jar", "lib2.jar"]

        mock_isdir.side_effect = [
            False
        ]

        snap_part = SnapPart(conf)
        self.assertRaises(SnapPartException, snap_part.generate_snap_part)

    def test_exception_on_invalid_part_type(self):
        conf = copy.deepcopy(self.conf)
        conf["PartType"] = "INVALID"
        conf["LibNames"] = ["lib1.jar", "lib2.jar"]

        snap_part = SnapPart(conf)
        self.assertRaises(SnapPartException, snap_part.generate_snap_part)

    def test_exception_on_invalid_config(self):
        conf = copy.deepcopy(self.conf)
        del conf["Logger"]
        self.assertRaises(SnapPartException, SnapPart, conf)
