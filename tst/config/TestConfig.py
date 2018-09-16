import unittest
import os
import json

from unittest.mock import patch, call
from modules.config.Config import ConfigException, Config
from tst.testutils.Mocks import MockFilePointer, MockLog


class TestConfig (unittest.TestCase):
    def setUp(self):
        self.config = {
            "GlobalPackageCache": os.path.join(os.environ["HOME"], ".packagecache"),
            "LogFile": os.path.join(os.environ["HOME"], ".bob", "bob.log"),
            "Level": "INFO"
        }
        self.md = {
            "Name": "TestPackage",
            "Version": "TestVersion",
            "BuildSystem": "ABC"
        }
        self.project_root = "ROOTZZ"

    @patch("modules.config.Config.Log", return_value=MockLog())
    @patch("builtins.open", autospec=True)
    @patch("os.path.isfile", return_value=True)
    @patch("os.path.isdir", return_value=True)
    def test_config_happy_case(self, mock_isdir, mock_isfile, mock_open, mock_log):
        mock_open.side_effect = [
            MockFilePointer(read_text=json.dumps(self.config, indent=4)),
            MockFilePointer(read_text=json.dumps(self.md, indent=4))
        ]
        config_obj = Config(self.project_root)
        actual_config = config_obj.get_config()
        self.assertEqual(self.config["GlobalPackageCache"], actual_config["GlobalPackageCache"])
        self.assertEqual(self.config["LogFile"], actual_config["LogFile"])
        self.assertEqual(self.config["Level"], actual_config["Level"])
        self.assertEqual(type(actual_config["Logger"]), type(MockLog()))
        self.assertEqual(self.md["BuildSystem"], actual_config["BuildSystem"])

        isfile_calls = [
            call(Config.CONFIG_FILE),
            call(os.path.join(self.project_root, "md.json"))
        ]
        mock_isfile.assert_has_calls(isfile_calls)

    @patch("modules.config.Config.Log", return_value=MockLog())
    @patch("builtins.open", autospec=True)
    @patch("os.path.isfile", autospec=True)
    @patch("os.makedirs", return_value=None)
    @patch("os.path.isdir", return_value=False)
    def test_config_creates_file_on_first_run(self, mock_isdir, mock_makedirs, mock_isfile, mock_open, mock_log):
        mock_isfile.side_effect = [False, True]
        write_fp = MockFilePointer(read_text="")
        read_fp = MockFilePointer(read_text=json.dumps(self.md, indent=4))
        mock_open.side_effect = [
            write_fp,
            read_fp
        ]
        Config(self.project_root)

        makedirs_calls = [call(Config.ROOT)]
        mock_makedirs.assert_has_calls(makedirs_calls)

        self.assertEqual(1, len(write_fp.invocations["write"]))
        self.assertEqual(self.config, json.loads(write_fp.invocations["write"][0]))

    @patch("modules.config.Config.Log", return_value=MockLog())
    @patch("builtins.open", autospec=True)
    @patch("os.path.isfile", autospec=True)
    @patch("os.makedirs", return_value=None)
    @patch("os.path.isdir", return_value=False)
    def test_exception_on_failure_to_create_file(self, mock_isdir, mock_makedirs, mock_isfile, mock_open, mock_log):
        mock_isfile.side_effect = [False, True]
        mock_open.side_effect = OSError()
        self.assertRaises(ConfigException, Config, self.project_root)

    @patch("modules.config.Config.Log", return_value=MockLog())
    @patch("builtins.open", autospec=True)
    @patch("os.path.isfile", autospec=True)
    @patch("os.makedirs", return_value=None)
    @patch("os.path.isdir", return_value=False)
    def test_exception_on_failure_to_read_file(self, mock_isdir, mock_makedirs, mock_isfile, mock_open, mock_log):
        mock_isfile.side_effect = [True, True]
        mock_open.side_effect = OSError()
        self.assertRaises(ConfigException, Config, self.project_root)

    @patch("modules.config.Config.Log", return_value=MockLog())
    @patch("builtins.open", autospec=True)
    @patch("os.path.isfile", autospec=True)
    @patch("os.path.isdir", return_value=False)
    def test_exception_on_malformed_json(self, mock_isdir, mock_isfile, mock_open, mock_log):
        mock_isfile.side_effect = [True, True]
        mock_open.side_effect = [
            MockFilePointer(read_text="Malformed meta-data")
        ]
        self.assertRaises(ConfigException, Config, self.project_root)

    @patch("modules.config.Config.Log", return_value=MockLog())
    @patch("builtins.open", autospec=True)
    @patch("os.path.isfile", autospec=True)
    @patch("os.makedirs", return_value=None)
    @patch("os.path.isdir", return_value=False)
    def test_exception_on_absent_md_json(self, mock_isdir, mock_makedirs, mock_isfile, mock_open, mock_log):
        mock_isfile.side_effect = [True, False]
        mock_open.side_effect = [
            MockFilePointer(read_text=json.dumps(self.config, indent=4)),
        ]
        self.assertRaises(ConfigException, Config, self.project_root)

    @patch("modules.config.Config.Log", return_value=MockLog())
    @patch("builtins.open", autospec=True)
    @patch("os.path.isfile", autospec=True)
    @patch("os.makedirs", return_value=None)
    @patch("os.path.isdir", return_value=False)
    def test_exception_on_un_openable_md_json(self, mock_isdir, mock_makedirs, mock_isfile, mock_open, mock_log):
        mock_isfile.side_effect = [True, True]
        mock_open.side_effect = [
            MockFilePointer(read_text=json.dumps(self.config, indent=4)),
            OSError()
        ]
        self.assertRaises(ConfigException, Config, self.project_root)


    @patch("modules.config.Config.Log", return_value=MockLog())
    @patch("builtins.open", autospec=True)
    @patch("os.path.isfile", autospec=True)
    @patch("os.makedirs", return_value=None)
    @patch("os.path.isdir", return_value=False)
    def test_exception_on_malformed_md(self, mock_isdir, mock_makedirs, mock_isfile, mock_open, mock_log):
        mock_isfile.side_effect = [True, True]
        mock_open.side_effect = [
            MockFilePointer(read_text=json.dumps(self.config, indent=4)),
            MockFilePointer(read_text="Malformed meta-data json.")
        ]
        self.assertRaises(ConfigException, Config, self.project_root)

    @patch("modules.config.Config.Log", return_value=MockLog())
    @patch("builtins.open", autospec=True)
    @patch("os.path.isfile", autospec=True)
    @patch("os.makedirs", return_value=None)
    @patch("os.path.isdir", return_value=False)
    def test_exception_on_no_name(self, mock_isdir, mock_makedirs, mock_isfile, mock_open, mock_log):
        mock_isfile.side_effect = [True, True]
        mock_open.side_effect = [
            MockFilePointer(read_text=json.dumps(self.config, indent=4)),
            MockFilePointer(read_text=json.dumps({"Version": "1.0", "BuildSystem": "ABC"}, indent=4))
        ]
        self.assertRaises(ConfigException, Config, self.project_root)

    @patch("modules.config.Config.Log", return_value=MockLog())
    @patch("builtins.open", autospec=True)
    @patch("os.path.isfile", autospec=True)
    @patch("os.makedirs", return_value=None)
    @patch("os.path.isdir", return_value=False)
    def test_exception_on_no_version(self, mock_isdir, mock_makedirs, mock_isfile, mock_open, mock_log):
        mock_isfile.side_effect = [True, True]
        mock_open.side_effect = [
            MockFilePointer(read_text=json.dumps(self.config, indent=4)),
            MockFilePointer(read_text=json.dumps({"Name": "Papaya", "BuildSystem": "ABC"}, indent=4))
        ]
        self.assertRaises(ConfigException, Config, self.project_root)

    @patch("modules.config.Config.Log", return_value=MockLog())
    @patch("builtins.open", autospec=True)
    @patch("os.path.isfile", autospec=True)
    @patch("os.makedirs", return_value=None)
    @patch("os.path.isdir", return_value=False)
    def test_exception_on_no_build_system(self, mock_isdir, mock_makedirs, mock_isfile, mock_open, mock_log):
        mock_isfile.side_effect = [True, True]
        mock_open.side_effect = [
            MockFilePointer(read_text=json.dumps(self.config, indent=4)),
            MockFilePointer(read_text=json.dumps({"Name": "Papaya", "Version": "1.0"}, indent=4))
        ]
        self.assertRaises(ConfigException, Config, self.project_root)
