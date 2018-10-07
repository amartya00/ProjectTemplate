import unittest
import copy

from unittest.mock import patch, call

from modules.package.Package import PackageException, Package
from tst.testutils.Mocks import MockLog, MockSnapPart, MockSnapCMake


class TestPackage (unittest.TestCase):
    def setUp(self):
        self.config = {
            "Logger": MockLog(),
            "LocalPackageCache": "PACKAGE_CACHE",
            "GlobalPackageCache": "GLOBAL_CACHE",
            "ProjectRoot": "ROOT",
            "BuildFolder": "BUILD",
            "Packaging": [
                {
                    "Type": "SnapPart",
                    "SnapPartType": "headers",
                    "HeadersSource": "myheaders",
                    "HeadersDest": "destheaders"
                },
                {
                    "Type": "SnapPart",
                    "SnapPartType": "headers",
                    "HeadersSource": "myheaders2",
                    "HeadersDest": "destheaders2"
                },
                {
                    "Type": "SnapCMake",
                    "OtherStuff": "The mock does not care about them"
                }
            ],
            "Dependencies": [],
            "BuildDeps": [
                {
                    "Name": "YY",
                    "Version": "0.0"
                }
            ],
            "RuntimeDeps": [],
            "TestDeps": []
        }

    @patch("os.path.isdir", return_value=True)
    @patch("modules.package.Package.SnapCMake", autospec=True)
    @patch("modules.package.Package.SnapPart", return_value=MockSnapPart())
    def test_package_happy_case(self, mock_snap_part, mock_snap_cmake, mock_isdir):
        mock_snap_cmake_process = MockSnapCMake()
        mock_snap_cmake.side_effect = [mock_snap_cmake_process]
        snap_part_calls = [
            call(self.config["Packaging"][0]),
            call(self.config["Packaging"][1])
        ]

        package = Package(self.config)
        package.package()

        # Validate snap part calls
        mock_snap_part.assert_has_calls(snap_part_calls, any_order=False)
        # Validate snap CMake calls
        self.assertEquals(1, mock_snap_cmake_process.invocations)

        isdir_calls = [
            call(self.config["BuildFolder"])
        ]
        mock_isdir.assert_has_calls(isdir_calls)

    @patch("os.path.isdir", return_value=True)
    def test_exception_on_no_package_info(self, mock_isdir):
        config = copy.deepcopy(self.config)
        del config["Packaging"]

        package = Package(config)
        self.assertRaises(PackageException, package.package)

    @patch("os.path.isdir", return_value=True)
    def test_exception_on_invalid_package_type(self, mock_isdir):
        config = copy.deepcopy(self.config)
        config["Packaging"][0]["Type"] = "INVALID"

        package = Package(config)
        self.assertRaises(PackageException, package.package)

    @patch("os.path.isdir", return_value=True)
    def test_exception_on_missing_package_type(self, mock_isdir):
        config = copy.deepcopy(self.config)
        del config["Packaging"][0]["Type"]

        package = Package(config)
        self.assertRaises(PackageException, package.package)

    @patch("os.path.isdir", return_value=True)
    @patch("modules.package.Package.SnapPart", autospec=True)
    def test_exception_on_snap_part_exception(self, mock_snap_part, mock_isdir):
        snap_part = MockSnapPart()
        snap_part.set_throws()
        mock_snap_part.side_effect = [snap_part]

        package = Package(self.config)
        self.assertRaises(PackageException, package.package)

    @patch("os.path.isdir", return_value=False)
    @patch("modules.package.Package.SnapPart", autospec=True)
    def test_exception_on_missing_build_folder(self, mock_snap_part, mock_isdir):
        snap_part = MockSnapPart()
        mock_snap_part.side_effect = [snap_part]

        package = Package(self.config)
        self.assertRaises(PackageException, package.package)

    @patch("os.path.isdir", return_value=True)
    @patch("modules.package.Package.SnapPart", return_value=MockSnapPart())
    def test_exception_on_invalid_config(self, mock_snap_part, mock_isdir):
        config = copy.deepcopy(self.config)
        del config["BuildFolder"]
        package = Package(config)
        self.assertRaises(PackageException, package.package)

        config["BuildFolder"] = "BUILD"
        del config["ProjectRoot"]
        self.assertRaises(PackageException, package.package)
