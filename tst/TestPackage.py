import os
import sys
import unittest
import json
import yaml

sys.dont_write_bytecode = True
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")

from unittest.mock import patch, call
from lib.Package import PackageException, Package
from tst.Mocks import MockLog, MockFilePointer, MockProcess


class TestPackage (unittest.TestCase):
    EXIT_SUCCESS = 0
    EXIT_FAILURE = 1

    @patch("os.path.isdir", return_value=True)
    @patch("builtins.open", autospec=True)
    def setUp(self, mock_open, mock_isdir):
        self.md = {
            "Packaging": {
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
            }
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

    @patch("os.path.isfile", autospec=True)
    def test_snappy_yaml(self, mock_isfile):
        mock_isfile.side_effect = [True, True, False, True]
        yaml_str = self.p.snappy_yaml()
        actual_yaml = yaml.load(yaml_str)
        # Test parts
        assert ("c" in actual_yaml["parts"].keys())
        assert ("b" in actual_yaml["parts"].keys())
        assert ("d" in actual_yaml["parts"].keys())
        assert ("e" in actual_yaml["parts"].keys())
        assert (self.md["Packaging"]["Name"] in actual_yaml["parts"].keys())
        assert (actual_yaml["name"] == self.md["Packaging"]["Name"])
        assert (actual_yaml["version"] == self.md["Packaging"]["Version"])
        assert (actual_yaml["summary"] == self.md["Packaging"]["Summary"])
        assert (actual_yaml["description"] == self.md["Packaging"]["Description"])
        assert (actual_yaml["confinement"] == self.md["Packaging"]["Confinement"])
        assert (actual_yaml["grade"] == self.md["Packaging"]["Grade"])
        assert (len(actual_yaml["apps"].keys()) == 1)
        assert (self.md["Packaging"]["Apps"][0]["Name"] in actual_yaml["apps"].keys())
        assert (self.md["Packaging"]["Apps"][0]["Command"] == actual_yaml["apps"][self.md["Packaging"]["Apps"][0]["Name"]]["command"])

    @patch("subprocess.Popen", autospec=True)
    def test_make_snap(self, mock_popen):
        p = MockProcess("OUT", "ERR", TestPackage.EXIT_SUCCESS)
        mock_popen.side_effect = [p]
        self.p.make_snap()
        popen_calls = [call(["snapcraft"])]
        mock_popen.assert_has_calls(popen_calls)