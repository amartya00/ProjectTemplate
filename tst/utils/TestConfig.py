import json
import os
import sys
import unittest
from unittest.mock import patch, call

sys.dont_write_bytecode = True
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")

from lib.utils.Config import Config
from tst.testutils.Mocks import MockFilePointer, MockLog


class TestConfig(unittest.TestCase):
    CONF_FILE_CONTENT = {
        "PackageCacheRoot": "TEST_ROOT",
        "BucketName": "TEST_BKT",
        "ProgramName": "TEST_PROG",
        "Level": "TEST_DEBUG",
        "LogFile": "TEST_LOG"
    }

    @patch("lib.utils.Config.Log", return_value=MockLog())
    @patch("os.path.isdir", return_value=False)
    @patch("os.makedirs", return_value=None)
    @patch("os.path.isfile", return_value=False)
    @patch("builtins.open", autospec=True)
    def test_first_run(self, mock_open, mock_isfile, mock_makedirs, mock_isdir, mock_log):
        fp_write_conf_file = MockFilePointer(None)
        fp_read_conf_file = MockFilePointer(read_text=json.dumps(TestConfig.CONF_FILE_CONTENT, indent=4))
        mock_open.side_effect = [fp_write_conf_file, fp_read_conf_file]
        conf = Config()
        self.assertTrue(conf)

        isdir_calls = [call(Config.DEFAULT_CONF_FOLDER)]
        makedirs_calls = [call(Config.DEFAULT_CONF_FOLDER)]
        isfile_calls = [call(Config.DEFAULT_CONF_FILE)]

        mock_isfile.assert_has_calls(isfile_calls)
        mock_isdir.assert_has_calls(isdir_calls)
        mock_makedirs.assert_has_calls(makedirs_calls)

        self.assertEqual(1, len(fp_write_conf_file.invocations["write"]))
        assert (fp_write_conf_file.invocations["write"][0] == json.dumps(Config.DEFAULT_CONF, indent=4))

    @patch("lib.utils.Config.Log", return_value=MockLog())
    @patch("os.path.isdir", return_value=True)
    @patch("os.path.isfile", return_value=True)
    @patch("builtins.open", autospec=True)
    def test_init_from_override(self, mock_open, mock_isfile, mock_isdir, mock_log):
        fp = MockFilePointer(read_text=json.dumps(TestConfig.CONF_FILE_CONTENT, indent=4))
        mock_open.side_effect = [fp]
        conf = Config("TEST_LOG")
        self.assertEqual(TestConfig.CONF_FILE_CONTENT, conf.conf)

    @patch("lib.utils.Config.Log", return_value=MockLog())
    @patch("os.path.isdir", return_value=True)
    @patch("os.path.isfile", return_value=True)
    @patch("builtins.open", autospec=True)
    def test_partial_init_from_override(self, mock_open, mock_isfile, mock_isdir, mock_log):
        partial_conf = dict(TestConfig.CONF_FILE_CONTENT)
        del partial_conf["PackageCacheRoot"]
        del partial_conf["Level"]
        fp = MockFilePointer(read_text=json.dumps(partial_conf, indent=4))
        mock_open.side_effect = [fp]
        conf = Config("TEST_LOG")
        self.assertEqual(partial_conf["BucketName"], conf.conf["BucketName"])
        self.assertEqual(partial_conf["ProgramName"], conf.conf["ProgramName"])
        self.assertEqual(partial_conf["LogFile"], conf.conf["LogFile"])
        self.assertEqual(Config.DEFAULT_CONF["PackageCacheRoot"], conf.conf["PackageCacheRoot"])
        self.assertEqual(Config.DEFAULT_CONF["Level"], conf.conf["Level"])

    @patch("lib.utils.Config.Log", return_value=MockLog())
    @patch("os.path.isdir", return_value=True)
    @patch("os.path.isfile", return_value=True)
    @patch("builtins.open", autospec=True)
    def test_init_no_override(self, mock_open, mock_isfile, mock_isdir, mock_log):
        fp = MockFilePointer(read_text=json.dumps(TestConfig.CONF_FILE_CONTENT, indent=4))
        mock_open.side_effect = [fp]
        conf = Config()
        self.assertEqual(TestConfig.CONF_FILE_CONTENT, conf.conf)
