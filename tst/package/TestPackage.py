import unittest
import copy

from unittest.mock import patch, call

from modules.package.Package import PackageException, Package
from tst.testutils.Mocks import MockLog, MockSnapPart


class TestPackage (unittest.TestCase):
    def setUp(self):
        self.config = {
            "Logger": MockLog(),
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
                }
            ]
        }

    @patch("modules.package.Package.SnapPart", return_value=MockSnapPart())
    def test_package_happy_case(self, mock_snap_part):
        package = Package(self.config)
        package.package()

        snap_part_calls = [
            call(self.config["Packaging"][0]),
            call(self.config["Packaging"][1])
        ]
        mock_snap_part.assert_has_calls(snap_part_calls, any_order=False)

    def test_exception_on_no_package_info(self):
        config = copy.deepcopy(self.config)
        del config["Packaging"]

        package = Package(config)
        self.assertRaises(PackageException, package.package)

    def test_exception_on_invalid_package_type(self):
        config = copy.deepcopy(self.config)
        config["Packaging"][0]["Type"] = "INVALID"

        package = Package(config)
        self.assertRaises(PackageException, package.package)

    @patch("modules.package.Package.SnapPart", autospec=True)
    def test_exception_on_snap_part_exception(self, mock_snap_part):
        snap_part = MockSnapPart()
        snap_part.set_throws()
        mock_snap_part.side_effect = [snap_part]

        package = Package(self.config)
        self.assertRaises(PackageException, package.package)
