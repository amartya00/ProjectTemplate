import json
import os
import sys
import unittest

import yaml

sys.dont_write_bytecode = True
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")

from unittest.mock import patch, call
from lib.package.Package import Package
from tst.testutils.Mocks import MockLog, MockFilePointer, MockProcess


class TestPackage(unittest.TestCase):
    EXIT_SUCCESS = 0
    EXIT_FAILURE = 1

    @patch("os.path.isdir", return_value=True)
    @patch("builtins.open", autospec=True)
    def setUp(self, mock_open, mock_isdir):
        self.md = {
            "Packaging": [
                {
                    "Name": "TEST_SNAP",
                    "Type": "snap",
                    "Version": "TEST_VERSTION",
                    "Summary": "Blah blah.",
                    "Description": "Blah blah.",
                    "Confinement": "CONFINEMENT",
                    "Grade": "GRADE",
                    "Apps": [
                        {
                            "Name": "SAMPLE_APP",
                            "Command": "SAMPLE_COMMAND"
                        }
                    ]
                },
                {
                    "Name": "TEST_SNAP_PART_LIB",
                    "Type": "snap-part",
                    "PartType": "lib",
                    "LibName": "liba.so"
                },
                {
                    "Name": "TEST_SNAP_PART_HEADER",
                    "Type": "snap-part",
                    "PartType": "headers",
                    "HeadersSource": "headers-src",
                    "HeadersDest": "HEADER_DEST"
                }
            ]
        }
        self.config = {
            "LocalPackageCache": "LOCAL",
            "PackageCacheRoot": "CACHE",
            "BucketName": "TEST_BKT",
            "ProjectDir": "PROJ_DIR"
        }
        self.dependencies = [
            {
                "Package": "c",
                "Version": "0.0"
            },
            {
                "Package": "b",
                "Version": "0.1"
            },
            {
                "Package": "d",
                "Version": "1.0"
            },
            {
                "Package": "e",
                "Version": "0.0"
            }
        ]

        mock_fp = MockFilePointer(read_text=json.dumps(self.dependencies, indent=4))
        mock_open.side_effect = [mock_fp]
        self.logger = MockLog()
        self.p = Package(md=self.md, conf=self.config, logger=self.logger)

    def test_snappy_yaml(self):
        yaml_str = self.p.snappy_yaml(self.md["Packaging"][0])
        actual_yaml = yaml.load(yaml_str)
        # Test parts
        assert ("c" in actual_yaml["parts"].keys())
        assert ("b" in actual_yaml["parts"].keys())
        assert ("d" in actual_yaml["parts"].keys())
        assert ("e" in actual_yaml["parts"].keys())
        assert (self.md["Packaging"][0]["Name"] in actual_yaml["parts"].keys())
        assert (actual_yaml["name"] == self.md["Packaging"][0]["Name"])
        assert (actual_yaml["version"] == self.md["Packaging"][0]["Version"])
        assert (actual_yaml["summary"] == self.md["Packaging"][0]["Summary"])
        assert (actual_yaml["description"] == self.md["Packaging"][0]["Description"])
        assert (actual_yaml["confinement"] == self.md["Packaging"][0]["Confinement"])
        assert (actual_yaml["grade"] == self.md["Packaging"][0]["Grade"])
        assert (len(actual_yaml["apps"].keys()) == 1)
        assert (self.md["Packaging"][0]["Apps"][0]["Name"] in actual_yaml["apps"].keys())
        assert (self.md["Packaging"][0]["Apps"][0]["Command"] ==
                actual_yaml["apps"][self.md["Packaging"][0]["Apps"][0]["Name"]]["command"])

    def test_cmake_lists_lib(self):
        actual_cmake_lists_txt = Package.make_cmake_lists_for_snap_part(self.md["Packaging"][1])
        expected_cmake_lists_txt = "cmake_minimum_required(VERSION 3.0)\n"
        expected_cmake_lists_txt = expected_cmake_lists_txt + "project(" + self.md["Packaging"][1]["Name"] + ")\n"
        expected_cmake_lists_txt = expected_cmake_lists_txt + "file(GLOB libs ${CMAKE_CURRENT_SOURCE_DIR}/*.so*)\n"
        expected_cmake_lists_txt = expected_cmake_lists_txt + "install(FILES ${libs} DESTINATION lib)"
        assert (expected_cmake_lists_txt == actual_cmake_lists_txt)

    def test_cmake_lists_headers(self):
        actual_cmake_lists_txt = Package.make_cmake_lists_for_snap_part(self.md["Packaging"][2])
        expected_cmake_lists_txt = "cmake_minimum_required(VERSION 3.0)\n"
        expected_cmake_lists_txt = expected_cmake_lists_txt + "project(" + self.md["Packaging"][2]["Name"] + ")\n"
        expected_cmake_lists_txt = expected_cmake_lists_txt + "install(DIRECTORY " + self.md["Packaging"][2]["HeadersDest"] + " DESTINATION headers USE_SOURCE_PERMISSIONS)"
        assert (expected_cmake_lists_txt == actual_cmake_lists_txt)

    @patch("subprocess.Popen", autospec=True)
    def test_make_snap(self, mock_popen):
        p = MockProcess("OUT", "ERR", TestPackage.EXIT_SUCCESS)
        mock_popen.side_effect = [p]
        self.p.make_snap(self.md["Packaging"][0])
        popen_calls = [call(["snapcraft"])]
        mock_popen.assert_has_calls(popen_calls)
