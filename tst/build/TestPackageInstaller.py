import json
import os
import subprocess
import sys
import unittest

sys.dont_write_bytecode = True
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")

from unittest.mock import patch, call
from tst.testutils.Mocks import MockLog, MockProcess, MockFilePointer

from lib.build.PackageInstaller import PackageInstaller, PackageInstallerException


class TestPackageInstaller(unittest.TestCase):
    TEST_PACKAGE = "TestPkg"
    TEST_VERSION = "PkgVersion"
    TEST_MD = {
        "Package": "TEST",
        "Version": "VERSION"
    }
    EXIT_SUCCESS = 0
    EXIT_FAILURE = 1

    @patch("os.getcwd", return_value="CWD")
    @patch("os.makedirs", return_value=None)
    def setUp(self, mock_makedirs, mock_cwd):
        self.config = {
            "PackageCacheRoot": "PKG_CACHE_ROOT",
            "LocalPackageCache": "LOCAL_CACHE"
        }
        self.logger = MockLog()
        self.installer = PackageInstaller(config=self.config, logger=self.logger)

    @patch("os.path.isfile", return_value=True)
    @patch("subprocess.Popen", autospec=True)
    @patch("os.chdir", return_value=None)
    def test_install(self, mock_chdir, mock_popen, mock_isfile):
        cmake_process = MockProcess("CMAKE_OUT", "CMAKE_ERR", TestPackageInstaller.EXIT_SUCCESS)
        make_process = MockProcess("MAKE_OUT", "MAKE_ERR", TestPackageInstaller.EXIT_SUCCESS)
        make_install_process = MockProcess("MAKE__INST_OUT", "MAKE_INST_ERR", TestPackageInstaller.EXIT_SUCCESS)

        mock_popen.side_effect = [cmake_process, make_process, make_install_process]
        self.installer.install(TestPackageInstaller.TEST_PACKAGE, TestPackageInstaller.TEST_VERSION)

        chdir_calls = [call(self.config[
                                "PackageCacheRoot"] + "/" + TestPackageInstaller.TEST_PACKAGE + "/" + TestPackageInstaller.TEST_VERSION),
                       call("CWD")]
        popen_calls = [
            call(["cmake", ".", "-DCMAKE_INSTALL_PREFIX=" + self.config["LocalPackageCache"]], stdout=subprocess.PIPE,
                 stderr=subprocess.PIPE),
            call(["make"], stdout=subprocess.PIPE, stderr=subprocess.PIPE),
            call(["make", "install"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ]
        mock_chdir.assert_has_calls(chdir_calls)
        mock_popen.assert_has_calls(popen_calls)

    @patch("os.path.isfile", return_value=True)
    @patch("subprocess.Popen", autospec=True)
    @patch("os.chdir", return_value=None)
    def test_failed_cmake(self, mock_chdir, mock_popen, mock_isfile):
        cmake_process = MockProcess("CMAKE_OUT", "CMAKE_ERR", TestPackageInstaller.EXIT_FAILURE)
        make_process = MockProcess("MAKE_OUT", "MAKE_ERR", TestPackageInstaller.EXIT_SUCCESS)
        make_install_process = MockProcess("MAKE__INST_OUT", "MAKE_INST_ERR", TestPackageInstaller.EXIT_SUCCESS)
        mock_popen.side_effect = [cmake_process, make_process, make_install_process]
        self.assertRaises(PackageInstallerException, self.installer.install, TestPackageInstaller.TEST_PACKAGE,
                          TestPackageInstaller.TEST_VERSION)

    @patch("os.path.isfile", return_value=True)
    @patch("subprocess.Popen", autospec=True)
    @patch("os.chdir", return_value=None)
    def test_failed_make(self, mock_chdir, mock_popen, mock_isfile):
        cmake_process = MockProcess("CMAKE_OUT", "CMAKE_ERR", TestPackageInstaller.EXIT_SUCCESS)
        make_process = MockProcess("MAKE_OUT", "MAKE_ERR", TestPackageInstaller.EXIT_FAILURE)
        make_install_process = MockProcess("MAKE__INST_OUT", "MAKE_INST_ERR", TestPackageInstaller.EXIT_SUCCESS)
        mock_popen.side_effect = [cmake_process, make_process, make_install_process]
        self.assertRaises(PackageInstallerException, self.installer.install, TestPackageInstaller.TEST_PACKAGE,
                          TestPackageInstaller.TEST_VERSION)

    @patch("os.path.isfile", return_value=True)
    @patch("subprocess.Popen", autospec=True)
    @patch("os.chdir", return_value=None)
    def test_failed_make_install(self, mock_chdir, mock_popen, mock_isfile):
        cmake_process = MockProcess("CMAKE_OUT", "CMAKE_ERR", TestPackageInstaller.EXIT_SUCCESS)
        make_process = MockProcess("MAKE_OUT", "MAKE_ERR", TestPackageInstaller.EXIT_SUCCESS)
        make_install_process = MockProcess("MAKE__INST_OUT", "MAKE_INST_ERR", TestPackageInstaller.EXIT_FAILURE)
        mock_popen.side_effect = [cmake_process, make_process, make_install_process]
        self.assertRaises(PackageInstallerException, self.installer.install, TestPackageInstaller.TEST_PACKAGE,
                          TestPackageInstaller.TEST_VERSION)

    @patch("os.path.isfile", return_value=True)
    @patch("builtins.open", autospec=True)
    @patch("os.path.isdir", return_value=True)
    def test_extract_md(self, mock_isdir, mock_open, mock_isfile):
        md_fp = MockFilePointer(json.dumps(TestPackageInstaller.TEST_MD, indent=4))
        mock_open.side_effect = [md_fp]
        md = self.installer.get_installed_md(TestPackageInstaller.TEST_PACKAGE, TestPackageInstaller.TEST_VERSION)
        mock_isdir.assert_called_with(self.config[
                                          "PackageCacheRoot"] + "/" + TestPackageInstaller.TEST_PACKAGE + "/" + TestPackageInstaller.TEST_VERSION)
        assert (md == TestPackageInstaller.TEST_MD)

    @patch("os.path.isfile", return_value=True)
    @patch("os.path.isdir", return_value=False)
    def test_extract_md_fail_no_dir(self, mock_isdir, mock_isfile):
        self.assertRaises(PackageInstallerException, self.installer.get_installed_md, TestPackageInstaller.TEST_PACKAGE,
                          TestPackageInstaller.TEST_VERSION)

    @patch("os.path.isfile", return_value=False)
    @patch("os.path.isdir", return_value=True)
    def test_extract_md_fails_no_file(self, mock_isdir, mock_open):
        self.assertRaises(PackageInstallerException, self.installer.get_installed_md, TestPackageInstaller.TEST_PACKAGE,
                          TestPackageInstaller.TEST_VERSION)
        self.assertRaises(Exception, self.installer.get_installed_md, TestPackageInstaller.TEST_PACKAGE,
                          TestPackageInstaller.TEST_VERSION)
