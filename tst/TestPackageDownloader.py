import unittest
import os
import sys


from unittest.mock import patch
from tst.Mocks import MockLog
from lib.PackageDownloader import PackageDownloaderException, PackageDownloader

sys.dont_write_bytecode = True
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")

from tst.Mocks import MockTarfilePointer

class TestPackageDownloader (unittest.TestCase):
    TEST_PKG = "a"
    TEST_VERSION = "0.0"
    def setUp(self):
        self.conf = {
            "PackageCacheRoot": "TEST_ROOT",
            "BucketName": "TEST_BUCKET"
        }
        self.logger = MockLog()
        self.p = PackageDownloader(self.conf, self.logger)

    @patch("os.makedirs", return_value =True)
    @patch("os.path.isdir", return_value=True)
    def test_prep_folders_cache_exists(self, isdir, makedirs):
        self.p.prep_folders()
        isdir.assert_called_with(self.conf["PackageCacheRoot"])
        assert not makedirs.called

    @patch("os.makedirs", return_va1lue=True)
    @patch("os.path.isdir", return_value=False)
    def test_prep_folders_new_cache(self, isdir, makedirs):
        self.p.prep_folders()
        isdir.assert_called_with(self.conf["PackageCacheRoot"])
        makedirs.assert_called_with(self.conf["PackageCacheRoot"])

    @patch("os.path.isdir", return_value=True)
    @patch("lib.PackageDownloader.wget", return_value=(None, None, True))
    def test_download_package(self, mock_wget, mock_isdir):
        self.p.download_package(TestPackageDownloader.TEST_PKG, TestPackageDownloader.TEST_VERSION)
        expected_url = "https://s3.amazonaws.com/" + self.conf["BucketName"] + "/" + TestPackageDownloader.TEST_PKG + "/" + TestPackageDownloader.TEST_VERSION + "/" + TestPackageDownloader.TEST_PKG + ".tar"
        expected_dest = self.conf["PackageCacheRoot"] + "/" + TestPackageDownloader.TEST_PKG + "/" + TestPackageDownloader.TEST_VERSION + "/" + TestPackageDownloader.TEST_PKG + ".tar"
        mock_wget.assert_called_with(expected_url, expected_dest)

    @patch("lib.PackageDownloader.wget", return_value=(None, None, False))
    def test_exception_on_wget_fail(self, mock_wget):
        self.assertRaises(PackageDownloaderException, self.p.download_package, TestPackageDownloader.TEST_PKG, TestPackageDownloader.TEST_VERSION)
        self.assertRaises(Exception, self.p.download_package, TestPackageDownloader.TEST_PKG, TestPackageDownloader.TEST_VERSION)

    @patch("tarfile.open", autospec=True)
    def test_extract_pkg(self, tfl):
        fp = MockTarfilePointer()
        tfl.side_effect = [fp]
        self.p.extract_package(TestPackageDownloader.TEST_PKG, TestPackageDownloader.TEST_VERSION)
        assert(len(fp.invocations["extractall"]) == 1)
        assert(fp.invocations["extractall"][0] == self.conf["PackageCacheRoot"] + "/" + TestPackageDownloader.TEST_PKG + "/" + TestPackageDownloader.TEST_VERSION)
        assert(len(fp.invocations["close"]) == 1)




