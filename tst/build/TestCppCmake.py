import unittest
import subprocess

from unittest.mock import patch, call
from tst.testutils.Mocks import MockLog, MockProcess
from modules.build.CppCmake import CppCmake, BuildException


class TestCppCmake (unittest.TestCase):
    EXIT_SUCCESS = 0
    EXIT_FAILURE = 1

    @patch("os.getcwd", return_value="CWD")
    def setUp(self, mock_getcwd):
        self.config_obj = {
            "ProjectRoot": "ROOT",
            "LocalPackageCache": "TEST_PACKAGE_CACHE",
            "BuildDir": "TEST_BUILD_DIR",
            "Logger": MockLog()
        }
        self.builder = CppCmake(self.config_obj)

    @patch("os.getcwd", return_value="CWD")
    @patch("os.chdir", return_value=None)
    @patch("os.path.isdir", return_value=False)
    @patch("subprocess.Popen", autospec=True)
    @patch("os.makedirs", return_value=None)
    def test_build_happy_case(self, mock_makedirs, mock_popen, mock_isdir, mock_chdir, mock_getcwd):
        # Mock popen calls
        p_cmake = MockProcess("OUT", "ERR", TestCppCmake.EXIT_SUCCESS)
        p_make = MockProcess("OUT", "ERR", TestCppCmake.EXIT_SUCCESS)

        # Argument captors
        makedirs_calls = [
            call(self.config_obj["BuildDir"])
        ]
        isdir_calls = [
            call(self.config_obj["BuildDir"])
        ]
        chdir_calls = [
            call(self.config_obj["BuildDir"]),
            call(self.config_obj["ProjectRoot"])
        ]
        popen_calls = [
            call(["cmake", self.config_obj["ProjectRoot"], "-DPACKAGE_CACHE=" + self.config_obj["LocalPackageCache"]],stdout=subprocess.PIPE),
            call(["make"])
        ]
        mock_popen.side_effect = [p_cmake, p_make]

        self.builder.build()
        mock_isdir.assert_has_calls(isdir_calls, any_order=False)
        mock_makedirs.assert_has_calls(makedirs_calls, any_order=False)
        mock_chdir.assert_has_calls(chdir_calls, any_order=False)
        mock_popen.assert_has_calls(popen_calls, any_order=False)

    @patch("os.getcwd", return_value="CWD")
    @patch("os.chdir", return_value=None)
    @patch("os.path.isdir", return_value=True)
    @patch("subprocess.Popen", autospec=True)
    def test_run_test_happy_case(self, mock_popen, mock_isdir, mock_chdir, mock_getcwd):
        # Mock popen calls
        p_make = MockProcess("OUT", "ERR", TestCppCmake.EXIT_SUCCESS)
        # Argument captors
        isdir_calls = [
            call(self.config_obj["BuildDir"])
        ]
        chdir_calls = [
            call(self.config_obj["BuildDir"]),
            call(self.config_obj["ProjectRoot"])
        ]
        popen_calls = [
            call(["make", "test"])
        ]
        mock_popen.side_effect = [p_make]

        self.builder.run_tests()
        mock_isdir.assert_has_calls(isdir_calls, any_order=False)
        mock_chdir.assert_has_calls(chdir_calls, any_order=False)
        mock_popen.assert_has_calls(popen_calls, any_order=False)

    @patch("shutil.rmtree", return_value=None)
    @patch("os.getcwd", return_value="CWD")
    @patch("os.chdir", return_value=None)
    @patch("os.path.isdir", return_value=True)
    @patch("subprocess.Popen", autospec=True)
    def test_clean_happy_case(self, mock_popen, mock_isdir, mock_chdir, mock_getcwd, mock_rmtree):
        # Mock popen calls
        p_make = MockProcess("OUT", "ERR", TestCppCmake.EXIT_SUCCESS)
        # Argument captors
        isdir_calls = [
            call(self.config_obj["BuildDir"])
        ]
        chdir_calls = [
            call(self.config_obj["BuildDir"]),
            call(self.config_obj["ProjectRoot"])
        ]
        popen_calls = [
            call(["make", "test"])
        ]
        mock_popen.side_effect = [p_make]

        rmtree_calls = [
            call(self.config_obj["BuildDir"]),
            call(self.config_obj["LocalPackageCache"])
        ]

        self.builder.run_tests()
        self.builder.clean()
        mock_isdir.assert_has_calls(isdir_calls, any_order=False)
        mock_chdir.assert_has_calls(chdir_calls, any_order=False)
        mock_popen.assert_has_calls(popen_calls, any_order=False)
        mock_rmtree.assert_has_calls(rmtree_calls)

    @patch("os.getcwd", return_value="CWD")
    @patch("os.chdir", return_value=None)
    @patch("os.path.isdir", autospec=True)
    @patch("subprocess.Popen", autospec=True)
    @patch("os.makedirs", return_value=None)
    def test_run_test_first_builds(self, mock_makedirs, mock_popen, mock_isdir, mock_chdir, mock_getcwd):
        # Mock popen calls
        p_cmake = MockProcess("OUT", "ERR", TestCppCmake.EXIT_SUCCESS)
        p_make = MockProcess("OUT", "ERR", TestCppCmake.EXIT_SUCCESS)
        p_make_test = MockProcess("OUT", "ERR", TestCppCmake.EXIT_SUCCESS)

        # Argument captors
        isdir_calls = [
            call(self.config_obj["BuildDir"]),
            call(self.config_obj["BuildDir"])
        ]
        makedirs_calls = [
            call(self.config_obj["BuildDir"])
        ]
        chdir_calls = [
            call(self.config_obj["BuildDir"]),
            call(self.config_obj["ProjectRoot"]),
            call(self.config_obj["BuildDir"]),
            call(self.config_obj["ProjectRoot"])
        ]
        popen_calls = [
            call(["cmake", self.config_obj["ProjectRoot"], "-DPACKAGE_CACHE=" + self.config_obj["LocalPackageCache"]], stdout=subprocess.PIPE),
            call(["make"]),
            call(["make", "test"])
        ]
        mock_popen.side_effect = [p_cmake, p_make, p_make_test]
        mock_isdir.side_effect = [False, False]

        self.builder.run_tests()
        mock_isdir.assert_has_calls(isdir_calls, any_order=False)
        mock_makedirs.assert_has_calls(makedirs_calls, any_order=False)
        mock_chdir.assert_has_calls(chdir_calls, any_order=False)
        mock_popen.assert_has_calls(popen_calls, any_order=False)

    @patch("os.getcwd", return_value="CWD")
    @patch("os.chdir", return_value=None)
    @patch("os.path.isdir", return_value=False)
    @patch("subprocess.Popen", autospec=True)
    @patch("os.makedirs", return_value=None)
    def test_exception_on_build_dir_errors(self, mock_makedirs, mock_popen, mock_isdir, mock_chdir, mock_getcwd):
        mock_makedirs.side_effect = OSError("Permission denied")
        self.assertRaises(BuildException, self.builder.build)

    @patch("os.getcwd", return_value="CWD")
    @patch("os.chdir", return_value=None)
    @patch("os.path.isdir", return_value=True)
    @patch("subprocess.Popen", autospec=True)
    @patch("os.makedirs", return_value=None)
    def test_exception_on_cmake_error(self, mock_makedirs, mock_popen, mock_isdir, mock_chdir, mock_getcwd):
        mock_popen.side_effect = OSError("No such file")
        self.assertRaises(BuildException, self.builder.build)

    @patch("os.getcwd", return_value="CWD")
    @patch("os.chdir", return_value=None)
    @patch("os.path.isdir", return_value=True)
    @patch("subprocess.Popen", autospec=True)
    @patch("os.makedirs", return_value=None)
    def test_exception_on_make_error_during_build(self, mock_makedirs, mock_popen, mock_isdir, mock_chdir, mock_getcwd):
        mock_popen.side_effect = [MockProcess("OUT", "ERR", TestCppCmake.EXIT_SUCCESS), OSError("No such file")]
        self.assertRaises(BuildException, self.builder.build)

    @patch("os.getcwd", return_value="CWD")
    @patch("os.chdir", return_value=None)
    @patch("os.path.isdir", return_value=True)
    @patch("subprocess.Popen", autospec=True)
    def test_exception_on_make_error_during_test(self, mock_popen, mock_isdir, mock_chdir, mock_getcwd):
        mock_popen.side_effect = OSError("No such file")
        self.assertRaises(BuildException, self.builder.run_tests)

