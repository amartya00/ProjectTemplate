import unittest
import copy
import yaml
import os

from tst.testutils.Mocks import MockLog, MockProcess, MockFilePointer, MockTemporaryDirectory
from unittest.mock import patch, call
from modules.package.SnapCMake import SnapCMakeException, SnapCMake


class TestSnapCMake (unittest.TestCase):
    def setUp(self):
        self.conf = {
            "Name": "TEST_PROJECT",
            "Version": "1.0",
            "LocalPackageCache": "PACKAGE_CACHE",
            "GlobalPackageCache": "GLOBAL_PACKAGE_CACHE",
            "ProjectRoot": "ROOT",
            "BuildFolder": "BUILD",
            "Logger": MockLog(),
            "Dependencies": [{"Name": "A", "Version": "1.0"}],
            "RuntimeDeps": [],
            "BuildDeps": [],
            "TestDeps": []
        }
        self.package_step = {
            "Version": "23.0",
            "Summary": "Test Snap",
            "Grade": "Alpha",
            "Confinement": "cl        assic",
            "Description": "Long description",
            "Apps": [
                {"Name": "MY_APP_1", "Command": "app1"},
                {"Name": "MY_APP_2", "Command": "app2"}
            ]
        }

    @patch("os.path.isfile", return_value=True)
    @patch("shutil.copyfile", return_value=None)
    @patch("os.listdir", autospec=True)
    @patch("subprocess.Popen", autospec=True)
    @patch("os.chdir", return_value=None)
    @patch("os.getcwd", return_value="CWD")
    @patch("builtins.open", autospec=True)
    @patch("os.makedirs", return_value=None)
    @patch("tempfile.TemporaryDirectory", autospec=True)
    def test_happy_case(
            self,
            mock_temp_dir,
            mock_makedirs,
            mock_open,
            mock_getcwd,
            mock_chdir,
            mock_subprocess,
            mock_listdir,
            mock_copyfile,
            mock_isfile):
        # Set up mocks
        mock_temp_dir.side_effect = [MockTemporaryDirectory("MY_TEMPORARY_DIRECTORY")]
        snap_yaml_fp = MockFilePointer()
        print()
        mock_open.side_effect = [snap_yaml_fp]

        snap_process = MockProcess("OUT", "ERR", 0)
        mock_subprocess.side_effect = [snap_process]

        dirs = ["papaya.snap"]
        mock_listdir.side_effect = [dirs]

        # Make the package call
        conf = copy.deepcopy(self.conf)
        for key in self.package_step:
            conf[key] = self.package_step[key]
        snapper = SnapCMake(conf)
        snapper.package()

        # Validate chdir to temp dir and back
        mock_chdir_calls = [call("MY_TEMPORARY_DIRECTORY"), call("CWD")]
        mock_chdir.assert_has_calls(mock_chdir_calls)

        # Validate creation of snapcraft.yaml file
        yaml_contents = yaml.load(snap_yaml_fp.invocations["write"][0])
        for key in self.package_step:
            # Skip checking the Apps section here
            if key != "Apps":
                self.assertEquals(self.package_step[key], yaml_contents[key.lower()])
        self.assertEquals(self.package_step["Apps"][0]["Command"], yaml_contents["apps"]["MY_APP_1"]["command"])
        self.assertEquals(self.package_step["Apps"][1]["Command"], yaml_contents["apps"]["MY_APP_2"]["command"])

        self.assertEquals("A", list(yaml_contents["parts"].keys())[0])
        self.assertEquals("cmake", yaml_contents["parts"]["A"]["plugin"])
        source = os.path.join(
            self.conf["GlobalPackageCache"],
            self.conf["Dependencies"][0]["Name"],
            self.conf["Dependencies"][0]["Version"],
            self.conf["Dependencies"][0]["Name"] + ".tar")
        self.assertEquals(source, yaml_contents["parts"]["A"]["source"])
        self.assertEquals(1, len(snap_yaml_fp.invocations["write"]))

        # Validate it called snapcraft command
        popen_calls = [call(["snapcraft"])]
        mock_subprocess.assert_has_calls(popen_calls)

        # Validate it copied the snap back to the build folder
        mock_copyfile_calls = [
            call(
                os.path.join("MY_TEMPORARY_DIRECTORY", "papaya.snap"),
                os.path.join(self.conf["BuildFolder"], "papaya.snap")
            )
        ]
        mock_copyfile.assert_has_calls(mock_copyfile_calls)

    def test_exception_on_missing_config_params(self):
        # Make the package call
        conf = copy.deepcopy(self.conf)
        del conf["LocalPackageCache"]
        for key in self.package_step:
            conf[key] = self.package_step[key]
        snapper = SnapCMake(conf)
        self.assertRaises(SnapCMakeException, snapper.package)

    @patch("os.path.isfile", return_value=True)
    @patch("shutil.copyfile", return_value=None)
    @patch("os.listdir", autospec=True)
    @patch("subprocess.Popen", autospec=True)
    @patch("os.chdir", return_value=None)
    @patch("os.getcwd", return_value="CWD")
    @patch("builtins.open", autospec=True)
    @patch("os.makedirs", return_value=None)
    @patch("tempfile.TemporaryDirectory", autospec=True)
    def test_exception_on_missing_snapcraft_binary(
            self,
            mock_temp_dir,
            mock_makedirs,
            mock_open,
            mock_getcwd,
            mock_chdir,
            mock_subprocess,
            mock_listdir,
            mock_copyfile,
            mock_isfile):
        # Set up mocks
        mock_temp_dir.side_effect = [MockTemporaryDirectory("MY_TEMPORARY_DIRECTORY")]
        snap_yaml_fp = MockFilePointer()
        mock_open.side_effect = [snap_yaml_fp]

        snap_process = MockProcess("OUT", "ERR", 0)
        mock_subprocess.side_effect = OSError()

        dirs = ["papaya.snap"]
        mock_listdir.side_effect = [dirs]

        # Make the package call
        conf = copy.deepcopy(self.conf)
        for key in self.package_step:
            conf[key] = self.package_step[key]
        snapper = SnapCMake(conf)
        self.assertRaises(SnapCMakeException, snapper.package)

    @patch("os.path.isfile", return_value=True)
    @patch("shutil.copyfile", return_value=None)
    @patch("os.listdir", autospec=True)
    @patch("subprocess.Popen", autospec=True)
    @patch("os.chdir", return_value=None)
    @patch("os.getcwd", return_value="CWD")
    @patch("builtins.open", autospec=True)
    @patch("os.makedirs", return_value=None)
    @patch("tempfile.TemporaryDirectory", autospec=True)
    def test_exception_on_failed_snapcraft_command(
            self,
            mock_temp_dir,
            mock_makedirs,
            mock_open,
            mock_getcwd,
            mock_chdir,
            mock_subprocess,
            mock_listdir,
            mock_copyfile,
            mock_isfile
    ):
        # Set up mocks
        mock_temp_dir.side_effect = [MockTemporaryDirectory("MY_TEMPORARY_DIRECTORY")]
        snap_yaml_fp = MockFilePointer()
        mock_open.side_effect = [snap_yaml_fp]

        snap_process = MockProcess("OUT", "ERR", 1)
        mock_subprocess.side_effect = [snap_process]

        dirs = ["papaya.snap"]
        mock_listdir.side_effect = [dirs]

        # Make the package call
        conf = copy.deepcopy(self.conf)
        for key in self.package_step:
            conf[key] = self.package_step[key]
        snapper = SnapCMake(conf)
        self.assertRaises(SnapCMakeException, snapper.package)
