import unittest
import json
import os
import subprocess

from tst.testutils.Mocks import MockLog, MockProcess, MockFilePointer
from modules.bootstrap.PackageInstaller import PackageInstallerException, PackageInstaller
from unittest.mock import patch, call


class TestPackageInstaller (unittest.TestCase):
    def setUp(self):
        self.conf = {
            "GlobalPackageCache": "GLOBAL_CACHE",
            "LocalPackageCache": "LOCAL_CACHE",
            "Logger": MockLog()
        }
        self.package_list = [
            {
                "Name": "A",
                "Version": "1.0"
            },
            {
                "Name": "B",
                "Version": "2.0"
            }
        ]
        self.md = {
            "A": {
                "Dependencies": [
                    {
                        "Name": "C",
                        "Version": "3.0"
                    }
                ],
                "TestDeps": [
                    {
                        "Name": "B",
                        "Version": "2.0"
                    }
                ]
            },
            "B": {
                "BuildDeps": [
                    {
                        "Name": "Z",
                        "Version": "1.0"
                    }
                ],
                "RuntimeDeps": [
                    {
                        "Name": "X",
                        "Version": "0.0"
                    }
                ]
            }
        }
        self.installer = PackageInstaller(self.conf)

    @patch("builtins.open", autospec=True)
    @patch("subprocess.Popen", return_value=MockProcess("OUT", "ERR", 0))
    @patch("os.chdir", return_value=None)
    @patch("os.getcwd", return_value="CWD")
    @patch("os.makedirs", return_value=None)
    @patch("os.path.isdir", autospec=True)
    def test_package_installer_happy_case(self, mock_isdir, mock_makedirs, mock_cwd, mock_chdir, mock_popen, mock_open):
        mock_isdir.side_effect = [
            True, # Global package cache first access
            False, # Local package cache first access

            True, # Global package cache second access
            True,  # Local package cache second access

            True,  # Global package cache third access
            True  # Local package cache third access
        ]
        md_file_A = MockFilePointer(read_text=json.dumps(self.md["A"]))
        md_file_B = MockFilePointer(read_text=json.dumps(self.md["B"]))
        mock_open.side_effect = [md_file_A, md_file_B]

        actual_deps = self.installer.install_packages(self.package_list)
        expexted_deps = {}
        for dep in self.md["A"]["Dependencies"] + self.md["A"]["TestDeps"] + self.md["B"]["RuntimeDeps"] + self.md["B"]["BuildDeps"]:
            expexted_deps[dep["Name"]] = dep
        self.assertEqual(expexted_deps, actual_deps)

        isdir_calls = [
            call(os.path.join(
                self.conf["GlobalPackageCache"],
                self.package_list[0]["Name"],
                self.package_list[0]["Version"]
            )),
            call(self.conf["LocalPackageCache"]),
            call(os.path.join(
                self.conf["GlobalPackageCache"],
                self.package_list[1]["Name"],
                self.package_list[1]["Version"]
            )),
            call(self.conf["LocalPackageCache"])
        ]
        mock_isdir.assert_has_calls(isdir_calls, any_order=False)

        makedirs_calls = [
            call(self.conf["LocalPackageCache"])
        ]
        mock_makedirs.assert_has_calls(makedirs_calls, any_order=False)

        def get_chdir_call(i):
            return [
                call(os.path.join(
                    self.conf["GlobalPackageCache"],
                    self.package_list[i]["Name"],
                    self.package_list[i]["Version"]
                )),
                call("CWD")
            ]*3
        chdir_calls = get_chdir_call(0) + get_chdir_call(1)
        mock_chdir.assert_has_calls(chdir_calls, any_order=False)

        popen_calls = [
                call(["cmake", ".", "-DCMAKE_INSTALL_PREFIX=" + self.conf["LocalPackageCache"]], stdout=subprocess.PIPE, stderr=subprocess.PIPE),
                call(["make"], stdout=subprocess.PIPE, stderr=subprocess.PIPE),
                call(["make", "install"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ] * 2
        mock_popen.assert_has_calls(popen_calls, any_order=False)

    @patch("builtins.open", autospec=True)
    @patch("subprocess.Popen", autospec=True)
    @patch("os.chdir", return_value=None)
    @patch("os.getcwd", return_value="CWD")
    @patch("os.makedirs", return_value=None)
    @patch("os.path.isdir", autospec=True)
    def test_exception_on_absent_package(self, mock_isdir, mock_makedirs, mock_cwd, mock_chdir, mock_popen, mock_open):
        mock_isdir.side_effect = [
            False,  # Global package cache first access
            False,  # Local package cache first access

            True,  # Global package cache second access
            True,  # Local package cache second access

            True,  # Global package cache third access
            True  # Local package cache third access
        ]
        md_file_A = MockFilePointer(read_text=json.dumps(self.md["A"]))
        md_file_B = MockFilePointer(read_text=json.dumps(self.md["B"]))
        mock_open.side_effect = [md_file_A, md_file_B]

        self.assertRaises(PackageInstallerException, self.installer.install_packages, self.package_list)

    @patch("builtins.open", autospec=True)
    @patch("subprocess.Popen", return_value=MockProcess("OUT", "ERR", 0))
    @patch("os.chdir", return_value=None)
    @patch("os.getcwd", return_value="CWD")
    @patch("os.makedirs", return_value=None)
    @patch("os.path.isdir", autospec=True)
    def test_exception_on_absent_cmake(self, mock_isdir, mock_makedirs, mock_cwd, mock_chdir, mock_popen, mock_open):
        mock_isdir.side_effect = [
            True,  # Global package cache first access
            False,  # Local package cache first access

            True,  # Global package cache second access
            True,  # Local package cache second access

            True,  # Global package cache third access
            True  # Local package cache third access
        ]
        mock_popen.side_effect = OSError()

        self.assertRaises(PackageInstallerException, self.installer.install_packages, self.package_list)

        popen_calls = [
                          call(["cmake", ".", "-DCMAKE_INSTALL_PREFIX=" + self.conf["LocalPackageCache"]],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                      ]
        mock_popen.assert_has_calls(popen_calls, any_order=False)

    @patch("builtins.open", autospec=True)
    @patch("subprocess.Popen", return_value=MockProcess("OUT", "ERR", 0))
    @patch("os.chdir", return_value=None)
    @patch("os.getcwd", return_value="CWD")
    @patch("os.makedirs", return_value=None)
    @patch("os.path.isdir", autospec=True)
    def test_exception_on_absent_make(self, mock_isdir, mock_makedirs, mock_cwd, mock_chdir, mock_popen, mock_open):
        mock_isdir.side_effect = [
            True,  # Global package cache first access
            False,  # Local package cache first access

            True,  # Global package cache second access
            True,  # Local package cache second access

            True,  # Global package cache third access
            True  # Local package cache third access
        ]
        mock_popen.side_effect = [MockProcess("OUT", "ERR", 0), OSError()]
        self.assertRaises(PackageInstallerException, self.installer.install_packages, self.package_list)

        popen_calls = [
            call(["cmake", ".", "-DCMAKE_INSTALL_PREFIX=" + self.conf["LocalPackageCache"]],
                 stdout=subprocess.PIPE, stderr=subprocess.PIPE),
            call(["make"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ]
        mock_popen.assert_has_calls(popen_calls, any_order=False)

    @patch("builtins.open", autospec=True)
    @patch("subprocess.Popen", return_value=MockProcess("OUT", "ERR", 0))
    @patch("os.chdir", return_value=None)
    @patch("os.getcwd", return_value="CWD")
    @patch("os.makedirs", return_value=None)
    @patch("os.path.isdir", autospec=True)
    def test_exception_on_failed_cmake(self, mock_isdir, mock_makedirs, mock_cwd, mock_chdir, mock_popen, mock_open):
        mock_isdir.side_effect = [
            True,  # Global package cache first access
            False,  # Local package cache first access

            True,  # Global package cache second access
            True,  # Local package cache second access

            True,  # Global package cache third access
            True  # Local package cache third access
        ]
        mock_popen.side_effect = [MockProcess("CMAKE_OUT", "ERR", 1)]
        self.assertRaises(PackageInstallerException, self.installer.install_packages, self.package_list)

        popen_calls = [
            call(["cmake", ".", "-DCMAKE_INSTALL_PREFIX=" + self.conf["LocalPackageCache"]],
                 stdout=subprocess.PIPE, stderr=subprocess.PIPE),
        ]
        mock_popen.assert_has_calls(popen_calls, any_order=False)

    @patch("builtins.open", autospec=True)
    @patch("subprocess.Popen", return_value=MockProcess("OUT", "ERR", 0))
    @patch("os.chdir", return_value=None)
    @patch("os.getcwd", return_value="CWD")
    @patch("os.makedirs", return_value=None)
    @patch("os.path.isdir", autospec=True)
    def test_exception_on_failed_make(self, mock_isdir, mock_makedirs, mock_cwd, mock_chdir, mock_popen, mock_open):
        mock_isdir.side_effect = [
            True,  # Global package cache first access
            False,  # Local package cache first access

            True,  # Global package cache second access
            True,  # Local package cache second access

            True,  # Global package cache third access
            True  # Local package cache third access
        ]
        mock_popen.side_effect = [MockProcess("CMAKE_OUT", "ERR", 0), MockProcess("MAKE_OUT", "ERR", 1)]
        self.assertRaises(PackageInstallerException, self.installer.install_packages, self.package_list)

        popen_calls = [
            call(["cmake", ".", "-DCMAKE_INSTALL_PREFIX=" + self.conf["LocalPackageCache"]],
                 stdout=subprocess.PIPE, stderr=subprocess.PIPE),
            call(["make"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ]
        mock_popen.assert_has_calls(popen_calls, any_order=False)

    @patch("builtins.open", autospec=True)
    @patch("subprocess.Popen", return_value=MockProcess("OUT", "ERR", 0))
    @patch("os.chdir", return_value=None)
    @patch("os.getcwd", return_value="CWD")
    @patch("os.makedirs", return_value=None)
    @patch("os.path.isdir", autospec=True)
    def test_exception_on_failed_make_install(self, mock_isdir, mock_makedirs, mock_cwd, mock_chdir, mock_popen, mock_open):
        mock_isdir.side_effect = [
            True,  # Global package cache first access
            False,  # Local package cache first access

            True,  # Global package cache second access
            True,  # Local package cache second access

            True,  # Global package cache third access
            True  # Local package cache third access
        ]
        mock_popen.side_effect = [MockProcess("CMAKE_OUT", "ERR", 0), MockProcess("MAKE_OUT", "ERR", 0), MockProcess("MAKE_INSTALL_OUT", "ERR", 1)]
        self.assertRaises(PackageInstallerException, self.installer.install_packages, self.package_list)

        popen_calls = [
            call(["cmake", ".", "-DCMAKE_INSTALL_PREFIX=" + self.conf["LocalPackageCache"]],
                 stdout=subprocess.PIPE, stderr=subprocess.PIPE),
            call(["make"], stdout=subprocess.PIPE, stderr=subprocess.PIPE),
            call(["make", "install"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ]
        mock_popen.assert_has_calls(popen_calls, any_order=False)

    @patch("builtins.open", autospec=True)
    @patch("subprocess.Popen", return_value=MockProcess("OUT", "ERR", 0))
    @patch("os.chdir", return_value=None)
    @patch("os.getcwd", return_value="CWD")
    @patch("os.makedirs", return_value=None)
    @patch("os.path.isdir", autospec=True)
    def test_exception_on_invalid_metadata_file(self, mock_isdir, mock_makedirs, mock_cwd, mock_chdir, mock_popen, mock_open):
        mock_isdir.side_effect = [
            True,  # Global package cache first access
            False,  # Local package cache first access

            True,  # Global package cache second access
            True,  # Local package cache second access

            True,  # Global package cache third access
            True  # Local package cache third access
        ]
        md_file_A = MockFilePointer(read_text="Bad json")
        md_file_B = MockFilePointer(read_text=json.dumps(self.md["B"]))
        mock_open.side_effect = [md_file_A, md_file_B]

        self.assertRaises(PackageInstallerException, self.installer.install_packages, self.package_list)

    @patch("builtins.open", autospec=True)
    @patch("subprocess.Popen", return_value=MockProcess("OUT", "ERR", 0))
    @patch("os.chdir", return_value=None)
    @patch("os.getcwd", return_value="CWD")
    @patch("os.makedirs", return_value=None)
    @patch("os.path.isdir", autospec=True)
    def test_exception_on_invalid_absent_file(self, mock_isdir, mock_makedirs, mock_cwd, mock_chdir, mock_popen,
                                                mock_open):
        mock_isdir.side_effect = [
            True,  # Global package cache first access
            False,  # Local package cache first access

            True,  # Global package cache second access
            True,  # Local package cache second access

            True,  # Global package cache third access
            True  # Local package cache third access
        ]
        md_file_A = OSError()
        md_file_B = MockFilePointer(read_text=json.dumps(self.md["B"]))
        mock_open.side_effect = [md_file_A, md_file_B]

        self.assertRaises(PackageInstallerException, self.installer.install_packages, self.package_list)

    def test_init_errors(self):
        self.assertRaises(PackageInstallerException, PackageInstaller, {})
        self.assertRaises(PackageInstallerException, PackageInstaller, 10)

