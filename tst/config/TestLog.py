import unittest

from modules.config.Log import LogException, Log

from unittest.mock import patch, call
from modules.config.Config import ConfigException, Config
from tst.testutils.Mocks import MockFilePointer, MockLog
from tst.testutils.Mocks import MockLogger, MockFilePointer


class TestLog (unittest.TestCase):
    @patch("builtins.open", autospec=True)
    @patch("logging.getLogger", autospec=True)
    def setUp(self, mock_log, mock_open):
        self.logger = MockLogger()
        mock_log.side_effect = [self.logger]
        mock_open.side_effect = [MockFilePointer()]
        self.log = Log({
            "ProgramName": "TEST",
            "Level": "DEBUG",
            "LogFile": "TEST_FILE"
        })

    def test_info(self):
        self.log.info("INFO1\nINFO2")
        self.assertEqual(["INFO1", "INFO2"], self.logger.infos)

    def test_warn(self):
        self.log.warn("WARN1\nWARN2")
        self.assertEqual(["WARN1", "WARN2"], self.logger.warns)

    def test_error(self):
        self.log.error("ERROR1\nERROR2")
        self.assertEqual(["ERROR1", "ERROR2"], self.logger.errors)

    def test_debug(self):
        self.log.debug("DBG1\nDBG2")
        self.assertEqual(["DBG1", "DBG2"], self.logger.debugs)

    @patch("builtins.open", autospec=True)
    @patch("logging.getLogger", autospec=True)
    def test_handles_streams(self, mock_log,  mock_open):
        logger = MockLogger()
        mock_log.side_effect = [logger]
        mock_open.side_effect = [MockFilePointer()]
        log = Log({
            "ProgramName": "TEST",
            "Level": "DEBUG",
            "LogFile": "TEST_FILE"
        })
        log.info(b"papaya\nmango")
        self.assertEqual(["papaya", "mango"], logger.infos)

    def test_bad_level(self):
        self.assertRaises(
            LogException,
            Log,
            {
                "ProgramName": "TEST",
                "Level": "BANANA",
                "LogFile": "TEST_FILE"
            })

    def test_exception_in_incomplete_config(self):
        self.assertRaises(
            LogException,
            Log,
            {
                "ProgramName": "TEST",
                "Level": "DEBUG"
            })
