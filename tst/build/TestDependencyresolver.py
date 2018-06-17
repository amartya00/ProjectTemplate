import io
import json
import unittest
from unittest.mock import patch

from lib.build.DependencyResolver import DependencyResolver

from tst.testutils.Mocks import MockPackageInstaller
from tst.testutils.Mocks import MockPackageDownloader
from tst.testutils.Mocks import MockLog


class TestDependencyResolver(unittest.TestCase):
    TEST_BKT = "test_bucket"
    # Needed to initialize DependencyResolver
    TEST_PKG = {
        "Package": "a",
        "Version": "0.0",
        "RuntimeDeps": [
            {
                "Package": "b",
                "Version": "0.1"
            }
        ],
        "BuildDeps": [
            {
                "Package": "c",
                "Version": "0.0"
            }
        ],
        "TestDeps": [
            {
                "Package": "d",
                "Version": "1.0"
            }
        ],
        "Dependencies": [
            {
                "Package": "b",
                "Version": "0.1"
            }
        ]
    }
    # Needed to mock the get_md function of PackageDownloader
    PKG_MAP = {
        ("a", "0.0"): TEST_PKG,
        ("b", "0.1"): {
            "Dependencies": [
                {"Package": "e", "Version": "0.0"}
            ]
        },
        ("c", "0.0"): {
            "Dependencies": [
                {"Package": "e", "Version": "0.0"}
            ]
        },
        ("d", "1.0"): {
            "Dependencies": [
                {"Package": "e", "Version": "0.0"}
            ]
        },
        ("e", "0.0"): {
            "Dependencies": []
        }
    }

    @patch("lib.build.DependencyResolver.os.path.isfile", return_value=True)
    @patch("builtins.open", autospec=True)
    def setUp(self, opn, isf):
        opn.side_effect = [io.StringIO(json.dumps(TestDependencyResolver.TEST_PKG, indent=4)) for i in range(0, 10)]
        self.config = {"BucketName": TestDependencyResolver.TEST_BKT, "LocalPackageCache": "CACHE"}
        self.logger = MockLog()
        self.dep = DependencyResolver(self.config, self.logger)

    def test_url_gen(self):
        self.assertEqual("https://s3.amazonaws.com/" +
                         TestDependencyResolver.TEST_BKT + "/" +
                         TestDependencyResolver.TEST_PKG["Package"] + "/" +
                         TestDependencyResolver.TEST_PKG["Version"] + "/" +
                         TestDependencyResolver.TEST_PKG["Package"] + ".tar",
                         self.dep.s3_url(TestDependencyResolver.TEST_PKG["Package"],
                                         TestDependencyResolver.TEST_PKG["Version"]))

    def test_extract_deps(self):
        extracted = DependencyResolver.extract_deps(TestDependencyResolver.TEST_PKG)
        expected = []
        expected.extend(TestDependencyResolver.TEST_PKG["Dependencies"])
        expected.extend(TestDependencyResolver.TEST_PKG["RuntimeDeps"])
        expected.extend(TestDependencyResolver.TEST_PKG["TestDeps"])
        expected.extend(TestDependencyResolver.TEST_PKG["BuildDeps"])

        assert (len(expected) == len(extracted))
        for pkg in expected:
            self.assertTrue(pkg in extracted)

    """
    Test plan:
    Patch PackageDownloader and PackageInstaller
    Test to see if get_package and install_package are called with all the packages:
        b, c, d and e
    """

    @patch("os.path.isfile", return_value=True)
    @patch("builtins.open", return_value=io.StringIO(json.dumps(TEST_PKG, indent=4)))
    @patch("lib.build.DependencyResolver.PackageDownloader", autospec=True)
    @patch("lib.build.DependencyResolver.PackageInstaller", autospec=True)
    def test_bfs(self, pkg_installer, pkg_downloader, opn, isf):
        mock_d = MockPackageDownloader(None, None)
        mock_i = MockPackageInstaller(None, None, TestDependencyResolver.PKG_MAP)
        pkg_downloader.side_effect = [mock_d]
        pkg_installer.side_effect = [mock_i]
        dep_test = DependencyResolver(self.config, self.logger)
        dep_test.bfs()

        self.assertEqual(5, len(dep_test.dependency_list))
        self.assertTrue({"Package": "a", "Version": "0.0"} in dep_test.dependency_list)
        self.assertTrue({"Package": "b", "Version": "0.1"} in dep_test.dependency_list)
        self.assertTrue({"Package": "c", "Version": "0.0"} in dep_test.dependency_list)
        self.assertTrue({"Package": "d", "Version": "1.0"} in dep_test.dependency_list)
        self.assertTrue({"Package": "e", "Version": "0.0"} in dep_test.dependency_list)
