import os
import sys
import unittest
import subprocess

sys.dont_write_bytecode = True
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")

from unittest.mock import patch, call
from tst.Mocks import MockLog
from lib.Build import BuildException, Build
from tst.Mocks import MockDependencyResolver, MockProcess


class TestBuild(unittest.TestCase):
    TEST_INSTALLED_LIBS = [
        "liba.so.1",
        "libb.so.1",
        "liba.so"
    ]
    EXIT_SUCCESS = 0
    EXIT_FAILURE = 1

    def setUp(self):
        self.config = {
            "BuildFolder": "TEST_BUILD",
            "LocalPackageCache": "LOCAL_CACHE",
            "ProjectDir": "PROJ_DIR"
        }
        self.logger = MockLog()
        self.builder = Build(config=self.config, logger=self.logger)

    @patch("lib.Build.DependencyResolver", autospec=True)
    def test_bootstrap(self, mock_resolver):
        r = MockDependencyResolver(None, None)
        mock_resolver.side_effect = [r]
        self.builder.bootstrap()
        assert(len(r.invocations["bfs"]) == 1)

    @patch("os.getcwd", return_value="CWD")
    @patch("os.chdir", return_value=None)
    @patch("os.listdir", return_value=TEST_INSTALLED_LIBS)
    @patch("os.path.isfile", autospec=True)
    @patch("os.symlink", return_value=None)
    def test_symlink_bootstrapped(self, mock_symlink, mock_isfile, mock_listdir, mock_chdir, mock_getcwd):
        mock_isfile.side_effect = [True, False]
        self.builder.symlink_bootstrapped_libs()

        chdir_calls = [call(self.config["LocalPackageCache"]), call("CWD")]
        listdir_calls = [call(self.config["LocalPackageCache"])]
        isfile_calls = [call("liba.so"), call("libb.so")]
        symlink_calls = [call("libb.so.1", "libb.so")]

        mock_chdir.assert_has_calls(chdir_calls, any_order=False)
        mock_listdir.assert_has_calls(listdir_calls, any_order=False)
        mock_isfile.assert_has_calls(isfile_calls, any_order=False)
        mock_symlink.assert_has_calls(symlink_calls, any_order=False)

    @patch("os.chdir", return_value=None)
    @patch("os.getcwd", return_value="CWD")
    @patch("os.path.isdir", return_value=False)
    @patch("os.makedirs", return_value=None)
    @patch("subprocess.Popen", autospec=True)
    def test_run_cmake(self, mock_subprocess, mock_makedirs, mock_isdir, mock_cwd, mock_chdir):
        p = MockProcess("OUT", "ERR", TestBuild.EXIT_SUCCESS)
        mock_subprocess.side_effect = [p]
        self.builder.run_cmake()
        popen_calls = [call(["cmake", self.config["ProjectDir"], "-DPACKAGE_CACHE=" + self.config["LocalPackageCache"]],
                             stdout=subprocess.PIPE)]
        isdir_calls = [call(self.config["BuildFolder"])]
        makedirs_calls = [call(self.config["BuildFolder"])]
        chdir_calls = [call(self.config["BuildFolder"]), call("CWD")]

        mock_isdir.assert_has_calls(isdir_calls, any_order=False)
        mock_makedirs.assert_has_calls(makedirs_calls, any_order=False)
        mock_subprocess.assert_has_calls(popen_calls, any_order=False)
        mock_chdir.assert_has_calls(chdir_calls)


    @patch("os.path.isdir", return_value=True)
    @patch("os.getcwd", return_value="CWD")
    @patch("os.chdir", return_value=None)
    @patch("subprocess.Popen", autospec=True)
    def test_run_make(self, mock_popen, mock_chdir, mock_getcwd, mock_isdir):
        p = MockProcess("OUT", "ERR", TestBuild.EXIT_SUCCESS)
        mock_popen.side_effect = [p]
        self.builder.run_make()

        popen_calls = [call(["make"])]
        chdir_calls = [call(self.config["BuildFolder"]), call("CWD")]
        mock_popen.assert_has_calls(popen_calls, any_order=False)
        mock_chdir.assert_has_calls(chdir_calls)

    @patch("os.path.isdir", return_value=False)
    def test_run_make_throws_no_build_folder(self, mock_isdir):
        self.assertRaises(BuildException, self.builder.run_make)
        self.assertRaises(Exception, self.builder.run_make)

    @patch("os.path.isdir", return_value=True)
    @patch("os.getcwd", return_value="CWD")
    @patch("os.chdir", return_value=None)
    @patch("subprocess.Popen", autospec=True)
    def test_run_tests(self, mock_popen, mock_chdir, mock_getcwd, mock_isdir):
        p = MockProcess("OUT", "ERR", TestBuild.EXIT_SUCCESS)
        mock_popen.side_effect = [p]
        self.builder.run_tests()

        popen_calls = [call(["make", "test"], stdout=subprocess.PIPE)]
        chdir_calls = [call(self.config["BuildFolder"]), call("CWD")]
        mock_popen.assert_has_calls(popen_calls, any_order=False)
        mock_chdir.assert_has_calls(chdir_calls)

    @patch("os.path.isdir", return_value=False)
    def test_run_tests_throws_no_build_folder(self, mock_isdir):
        self.assertRaises(BuildException, self.builder.run_tests)
        self.assertRaises(Exception, self.builder.run_tests)

    @patch("os.path.isdir", return_value=True)
    @patch("shutil.rmtree", return_value=None)
    def test_clean(self, mock_rmtree, mock_isdir):
        self.builder.clean()

        isdir_calls = [call(self.config["BuildFolder"]), call(self.config["LocalPackageCache"])]
        rmtree_calls = [call(self.config["BuildFolder"]), call(self.config["LocalPackageCache"])]

        mock_isdir.assert_has_calls(isdir_calls, any_order=True)
        mock_rmtree.assert_has_calls(rmtree_calls, any_order=True)

    @patch("os.path.isdir", return_value=False)
    @patch("shutil.rmtree", return_value=None)
    def test_clean_no_folders(self, mock_rmtree, mock_isdir):
        self.builder.clean()

        isdir_calls = [call(self.config["BuildFolder"]), call(self.config["LocalPackageCache"])]

        mock_isdir.assert_has_calls(isdir_calls, any_order=True)
        assert(not mock_rmtree.called)






