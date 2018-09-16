import unittest
import os
import subprocess

from modules.bootstrap.PackageDownloader import PackageDownloaderException, PackageDownloader
from tst.testutils.Mocks import MockS3Client, MockLog, MockProcess, MockTarfilePointer, MockFilePointer
from unittest.mock import patch, call


class TestPackageDownloader (unittest.TestCase):
    EXIT_SUCCESS = 0
    EXIT_FAILURE = 1

    @patch("boto3.client", return_value=MockS3Client())
    def setUp(self, mock_s3_client):
        self.config_obj = {
            "GlobalPackageCache": "TEST_PKG_CACHE",
            "PackageSource": {
                "Type": "URL",
                "Url": "https://my_ftp_site/folder"
            },
            "Logger": MockLog()
        }
        self.package_list = [
            {
                "Name": "A",
                "Version": "1.0"
            },
            {
                "Name": "B",
                "Version": "2.0",
                "PackageSource": {
                    "Type": "S3",
                    "Bucket": "MY_BUCKET"
                }
            },
            {
                "Name": "C",
                "Version": "3.0",
                "PackageSource": {
                    "Type": "URL",
                    "Url": "https://test_ftp"
                }
            }
        ]
        self.downloader = PackageDownloader(self.config_obj)

    @patch("os.path.isdir", autospec=True)
    @patch("os.makedirs", return_value=None)
    @patch("subprocess.Popen", autospec=True)
    @patch("tarfile.open", autospec=True)
    @patch("builtins.open", autospec=True)
    def test_packages_downloaded_happy_case(self, mock_file, mock_tarfile, mock_popen, mock_makedirs, mock_isdir):
        # Mocks
        wget_1 = MockProcess("ERR", "OUT", TestPackageDownloader.EXIT_FAILURE)
        wget_2 = MockProcess("ERR", "OUT", TestPackageDownloader.EXIT_SUCCESS)
        tarfile_open = MockTarfilePointer()
        file_open = MockFilePointer()

        # Argument captors
        isdir_calls = [
            call(self.config_obj["GlobalPackageCache"])
        ]
        makedirs_calls = [
            call(self.config_obj["GlobalPackageCache"])
        ]
        wget_url_1 = "/".join([
            self.config_obj["PackageSource"]["Url"],
            self.package_list[0]["Name"],
            self.package_list[0]["Version"],
            self.package_list[0]["Name"] + ".tar"
        ])
        dest_1 = os.path.join(
            self.config_obj["GlobalPackageCache"],
            self.package_list[0]["Name"],
            self.package_list[0]["Version"],
            self.package_list[0]["Name"] + ".tar"
        )

        wget_url_2 = "/".join([
            self.package_list[2]["PackageSource"]["Url"],
            self.package_list[2]["Name"],
            self.package_list[2]["Version"],
            self.package_list[2]["Name"] + ".tar"
        ])
        dest_2 = os.path.join(
            self.config_obj["GlobalPackageCache"],
            self.package_list[2]["Name"],
            self.package_list[2]["Version"],
            self.package_list[2]["Name"] + ".tar"
        )
        popen_calls = [
            call(["wget", wget_url_1, "-O", dest_1], stdout=subprocess.PIPE, stderr=subprocess.PIPE),
            call(["wget", wget_url_2, "-O", dest_2], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ]
        s3_key = os.path.join(
            self.package_list[1]["Name"],
            self.package_list[1]["Version"],
            self.package_list[1]["Name"] + ".tar"
        )
        tarfile_opens = [
            os.path.join(
                self.config_obj["GlobalPackageCache"],
                self.package_list[0]["Name"],
                self.package_list[0]["Version"]
            ),
            os.path.join(
                self.config_obj["GlobalPackageCache"],
                self.package_list[1]["Name"],
                self.package_list[1]["Version"]
            ),
            os.path.join(
                self.config_obj["GlobalPackageCache"],
                self.package_list[2]["Name"],
                self.package_list[2]["Version"]
            )
        ]

        mock_isdir.side_effect = [False, True, True]
        mock_tarfile.side_effect = [tarfile_open, tarfile_open, tarfile_open]
        mock_file.side_effect = [file_open]
        mock_popen.side_effect = [wget_1, wget_2]

        self.downloader.download_and_extract(self.package_list)

        mock_isdir.assert_has_calls(isdir_calls, any_order=False)
        mock_makedirs.assert_has_calls(makedirs_calls, any_order=False)
        mock_popen.assert_has_calls(popen_calls)
        self.assertEqual(1, len(self.downloader.s3_client.invocations))
        self.assertEqual((self.package_list[1]["PackageSource"]["Bucket"], s3_key, file_open), self.downloader.s3_client.invocations[0])
        self.assertEqual(tarfile_opens, tarfile_open.invocations["extractall"])

    @patch("os.path.isdir", return_value=True)
    @patch("os.makedirs", return_value=None)
    @patch("subprocess.Popen", autospec=True)
    @patch("tarfile.open", autospec=True)
    @patch("builtins.open", autospec=True)
    def test_exception_on_failed_wget(self, mock_file, mock_tarfile, mock_popen, mock_makedirs, mock_isdir):
        wget_1 = MockProcess("ERR", "ERROR occured", TestPackageDownloader.EXIT_FAILURE)
        wget_2 = MockProcess("ERR", "OUT", TestPackageDownloader.EXIT_SUCCESS)
        mock_popen.side_effect = [wget_1, wget_2]
        self.assertRaises(PackageDownloaderException, self.downloader.download_and_extract, self.package_list)

    @patch("os.path.isdir", return_value=False)
    @patch("os.makedirs", autospec=True)
    @patch("subprocess.Popen", autospec=True)
    @patch("tarfile.open", autospec=True)
    @patch("builtins.open", autospec=True)
    def test_exception_on_fail_create_cache(self, mock_file, mock_tarfile, mock_popen, mock_makedirs, mock_isdir):
        mock_makedirs.side_effect = OSError()
        self.assertRaises(PackageDownloaderException, self.downloader.download_and_extract, self.package_list)

    @patch("os.path.isdir", return_value=True)
    @patch("os.makedirs", return_value=None)
    @patch("subprocess.Popen", autospec=True)
    @patch("tarfile.open", autospec=True)
    @patch("builtins.open", autospec=True)
    @patch("boto3.client", return_value=MockS3Client())
    def test_exception_on_failed_s3_download(self, mock_s3, mock_file, mock_tarfile, mock_popen, mock_makedirs, mock_isdir):
        # Mocks
        wget_1 = MockProcess("ERR", "OUT", TestPackageDownloader.EXIT_FAILURE)
        wget_2 = MockProcess("ERR", "OUT", TestPackageDownloader.EXIT_SUCCESS)
        tarfile_open = MockTarfilePointer()
        file_open = MockFilePointer()

        mock_tarfile.side_effect = [tarfile_open, tarfile_open, tarfile_open]
        mock_file.side_effect = [file_open]
        mock_popen.side_effect = [wget_1, wget_2]

        downloader = PackageDownloader(self.config_obj)

        downloader.s3_client.set_up_client_error()
        self.assertRaises(PackageDownloaderException, downloader.download_and_extract, self.package_list)

    @patch("os.path.isdir", return_value=True)
    @patch("os.makedirs", return_value=None)
    @patch("subprocess.Popen", autospec=True)
    @patch("tarfile.open", autospec=True)
    @patch("builtins.open", autospec=True)
    @patch("os.path.isfile", autospec=True)
    def test_not_downloaded_on_existing_package(self, mock_isfile, mock_file, mock_tarfile, mock_popen, mock_makedirs, mock_isdir):
        # Mocks
        wget_1 = MockProcess("ERR", "OUT", TestPackageDownloader.EXIT_FAILURE)
        wget_2 = MockProcess("ERR", "OUT", TestPackageDownloader.EXIT_SUCCESS)
        tarfile_open = MockTarfilePointer()
        file_open = MockFilePointer()

        # Argument captors
        isdir_calls = [
            call(self.config_obj["GlobalPackageCache"])
        ]
        makedirs_calls = []
        wget_url_1 = "/".join([
            self.config_obj["PackageSource"]["Url"],
            self.package_list[0]["Name"],
            self.package_list[0]["Version"],
            self.package_list[0]["Name"] + ".tar"
        ])
        dest_1 = os.path.join(
            self.config_obj["GlobalPackageCache"],
            self.package_list[0]["Name"],
            self.package_list[0]["Version"],
            self.package_list[0]["Name"] + ".tar"
        )

        wget_url_2 = "/".join([
            self.package_list[2]["PackageSource"]["Url"],
            self.package_list[2]["Name"],
            self.package_list[2]["Version"],
            self.package_list[2]["Name"] + ".tar"
        ])
        dest_2 = os.path.join(
            self.config_obj["GlobalPackageCache"],
            self.package_list[2]["Name"],
            self.package_list[2]["Version"],
            self.package_list[2]["Name"] + ".tar"
        )
        popen_calls = [
            call(["wget", wget_url_1, "-O", dest_1], stdout=subprocess.PIPE, stderr=subprocess.PIPE),
            call(["wget", wget_url_2, "-O", dest_2], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ]
        s3_key = os.path.join(
            self.package_list[1]["Name"],
            self.package_list[1]["Version"],
            self.package_list[1]["Name"] + ".tar"
        )
        tarfile_opens = [
            os.path.join(
                self.config_obj["GlobalPackageCache"],
                self.package_list[0]["Name"],
                self.package_list[0]["Version"]
            ),
            os.path.join(
                self.config_obj["GlobalPackageCache"],
                self.package_list[1]["Name"],
                self.package_list[1]["Version"]
            ),
            os.path.join(
                self.config_obj["GlobalPackageCache"],
                self.package_list[2]["Name"],
                self.package_list[2]["Version"]
            )
        ]

        mock_isfile.side_effect = [False, True, False]
        mock_tarfile.side_effect = [tarfile_open, tarfile_open, tarfile_open]
        mock_file.side_effect = [file_open]
        mock_popen.side_effect = [wget_1, wget_2]

        self.downloader.download_and_extract(self.package_list)

        mock_isdir.assert_has_calls(isdir_calls, any_order=False)
        mock_makedirs.assert_has_calls(makedirs_calls, any_order=False)
        mock_popen.assert_has_calls(popen_calls)
        self.assertEqual(0, len(self.downloader.s3_client.invocations))
        self.assertEqual(tarfile_opens, tarfile_open.invocations["extractall"])

    def test_initialization_fail(self):
        self.assertRaises(PackageDownloaderException, PackageDownloader, 10)
        self.assertRaises(PackageDownloaderException, PackageDownloader, {})

    @patch("os.path.isdir", return_value=True)
    @patch("boto3.client", return_value=MockS3Client())
    def test_malformed_data(self, mock_boto3, mock_isdir):
        pkg_list = [
            {
                "Name": "A",
                "Version": "1.0",
                "PackageSource": {
                    "Type": "S3",
                    "BucketZZ": "MY_BUCKET"
                }
            }
        ]
        downloader = PackageDownloader(self.config_obj)
        self.assertRaises(PackageDownloaderException, downloader.download_and_extract, pkg_list)

    @patch("os.path.isdir", return_value=True)
    @patch("boto3.client", return_value=MockS3Client())
    def test_invalid_data(self, mock_boto3, mock_isdir):
        pkg_list = [
            {
                "Name": "A",
                "Version": "1.0",
                "PackageSource": 10
            }
        ]
        downloader = PackageDownloader(self.config_obj)
        self.assertRaises(PackageDownloaderException, downloader.download_and_extract, pkg_list)

    @patch("os.path.isdir", return_value=True)
    @patch("os.makedirs", return_value=None)
    @patch("subprocess.Popen", autospec=True)
    @patch("tarfile.open", autospec=True)
    @patch("builtins.open", autospec=True)
    def test_exception_on_failure_to_extract(self, mock_file, mock_tarfile, mock_popen, mock_makedirs, mock_isdir):
        # Mocks
        wget_1 = MockProcess("ERR", "OUT", TestPackageDownloader.EXIT_FAILURE)
        wget_2 = MockProcess("ERR", "OUT", TestPackageDownloader.EXIT_SUCCESS)
        tarfile_open = MockTarfilePointer()
        tarfile_open.set_exception()
        file_open = MockFilePointer()

        mock_tarfile.side_effect = [tarfile_open, tarfile_open, tarfile_open]
        mock_file.side_effect = [file_open]
        mock_popen.side_effect = [wget_1, wget_2]

        self.assertRaises(PackageDownloaderException, self.downloader.download_and_extract, self.package_list)

    @patch("os.path.isdir", return_value=True)
    @patch("os.makedirs", return_value=None)
    @patch("subprocess.Popen", autospec=True)
    @patch("tarfile.open", autospec=True)
    @patch("builtins.open", autospec=True)
    def test_exception_on_absent_wget(self, mock_file, mock_tarfile, mock_popen, mock_makedirs, mock_isdir):
        mock_popen.side_effect = OSError()
        self.assertRaises(PackageDownloaderException, self.downloader.download_and_extract, self.package_list)


