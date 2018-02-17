import os
import sys
import unittest

sys.dont_write_bytecode = True
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")

from unittest.mock import patch
from tst.Mocks import MockLog
from lib.PackageDownloader import PackageDownloaderException, PackageDownloader
from tst.Mocks import MockTarfilePointer


class TestPackageDownloader(unittest.TestCase):
    TEST_PKG = "a"
    TEST_VERSION = "0.0"

    @patch("os.makedirs", return_value=None)
    def setUp(self, mkdirs):
        self.conf = {
            "PackageCacheRoot": "TEST_ROOT",
            "BucketName": "TEST_BUCKET"
        }
        self.logger = MockLog()
        self.p = PackageDownloader(self.conf, self.logger)

    @patch("os.makedirs", return_value=None)
    @patch("os.path.isdir", return_value=True)
    def test_prep_folders_cache_exists(self, isdir, makedirs):
        self.p.prep_folders()
        isdir.assert_called_with(self.conf["PackageCacheRoot"])
        assert not makedirs.called

    @patch("os.makedirs", return_va1lue=None)
    @patch("os.path.isdir", return_value=False)
    def test_prep_folders_new_cache(self, isdir, makedirs):
        self.p.prep_folders()
        isdir.assert_called_with(self.conf["PackageCacheRoot"])
        makedirs.assert_called_with(self.conf["PackageCacheRoot"])

    @patch("os.path.isdir", return_value=True)
    @patch("lib.PackageDownloader.wget", return_value=(None, None, True))
    @patch("os.makedirs", return_value=None)
    def test_download_package(self, mkdirs, mock_wget, mock_isdir):
        self.p.download_package(TestPackageDownloader.TEST_PKG, TestPackageDownloader.TEST_VERSION)
        expected_url = "https://s3.amazonaws.com/" + self.conf[
            "BucketName"] + "/" + TestPackageDownloader.TEST_PKG + "/" + TestPackageDownloader.TEST_VERSION + "/" + TestPackageDownloader.TEST_PKG + ".tar"
        expected_dest = self.conf[
                            "PackageCacheRoot"] + "/" + TestPackageDownloader.TEST_PKG + "/" + TestPackageDownloader.TEST_VERSION + "/" + TestPackageDownloader.TEST_PKG + ".tar"
        mock_wget.assert_called_with(expected_url, expected_dest)

    @patch("os.path.isdir", return_value=True)
    @patch("os.makedirs", return_value=None)
    @patch("lib.PackageDownloader.wget", return_value=(None, None, False))
    def test_exception_on_wget_fail(self, mock_wget, mock_makedirs, modk_isdir):
        self.assertRaises(PackageDownloaderException, self.p.download_package, TestPackageDownloader.TEST_PKG,
                          TestPackageDownloader.TEST_VERSION)
        self.assertRaises(Exception, self.p.download_package, TestPackageDownloader.TEST_PKG,
                          TestPackageDownloader.TEST_VERSION)

    @patch("tarfile.open", autospec=True)
    def test_extract_pkg(self, tfl):
        fp = MockTarfilePointer()
        tfl.side_effect = [fp]
        self.p.extract_package(TestPackageDownloader.TEST_PKG, TestPackageDownloader.TEST_VERSION)
        assert (len(fp.invocations["extractall"]) == 1)
        assert (fp.invocations["extractall"][0] == self.conf[
            "PackageCacheRoot"] + "/" + TestPackageDownloader.TEST_PKG + "/" + TestPackageDownloader.TEST_VERSION)
        assert (len(fp.invocations["close"]) == 1)
