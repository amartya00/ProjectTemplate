import unittest

from unittest.mock import patch
from tst.testutils.Mocks import MockPackageDownloader, MockPackageInstaller, MockLog
from modules.bootstrap.DependencyResolver import DependencyResolverException, DependencyResolver
from modules.bootstrap.PackageInstaller import PackageInstallerException
from modules.bootstrap.PackageDownloader import PackageDownloaderException


class TestDependencyResolver (unittest.TestCase):
    @patch("modules.bootstrap.DependencyResolver.PackageInstaller", autospec=True)
    @patch("modules.bootstrap.DependencyResolver.PackageDownloader", autospec=True)
    def setUp(self, mock_package_downloader, mock_package_installers):
        returned_dependencies = [
            {"A": {"Name": "A", "Version": "1.0"}, "B": {"Name": "B", "Version": "2.0"}},
            {"A": {"Name": "A", "Version": "1.0"}, "C": {"Name": "C", "Version": "3.0"}},
            {"A": {"Name": "B", "Version": "2.0"}, "C": {"Name": "C", "Version": "3.0"}}
        ]
        mock_package_downloader.side_effect = [MockPackageDownloader()]
        mock_package_installers.side_effect = [MockPackageInstaller(returned_dependencies)]
        self.config_obj = {
            "Dependencies": [{"Name": "D1", "Version": "1.0"}],
            "BuildDeps": [{"Name": "D2", "Version": "1.0"}],
            "RuntimeDeps": [{"Name": "D3", "Version": "1.0"}],
            "TestDeps": [{"Name": "D2", "Version": "1.0"}],
            "Logger": MockLog()
        }
        self.resolver = DependencyResolver(self.config_obj)

    def test_dependency_resolve_happy_case(self):
        actual_dependency_closure = self.resolver.bfs()
        expected_dependency_closure = [
            {"Name": "A", "Version": "1.0"},
            {"Name": "B", "Version": "2.0"},
            {"Name": "C", "Version": "3.0"},
            {"Name": "D1", "Version": "1.0"},
            {"Name": "D2", "Version": "1.0"},
            {"Name": "D3", "Version": "1.0"}
        ]
        self.assertEqual(sorted(expected_dependency_closure, key=lambda x: x["Name"]), sorted(actual_dependency_closure, key=lambda x: x["Name"]))

    @patch("modules.bootstrap.DependencyResolver.PackageInstaller", autospec=True)
    @patch("modules.bootstrap.DependencyResolver.PackageDownloader", autospec=True)
    def test_exception_on_bad_md(self, mock_package_downloader, mock_package_installers):
        returned_dependencies = [
            {"A": {"Name": "A", "Version": "1.0"}, "B": {"Name": "B", "Version": "2.0"}},
            {"A": {"Name": "A", "Version": "1.0"}, "C": {"Name": "C", "Version": "3.0"}},
            {"A": {"Name": "B", "Version": "2.0"}, "C": {"Name": "C", "Version": "3.0"}}
        ]
        mock_package_downloader.side_effect = [MockPackageDownloader()]
        mock_package_installers.side_effect = [MockPackageInstaller(returned_dependencies)]
        self.config_obj = {
            "Dependencies": [{"Name": "D1", "Version": "1.0"}],
            "BuildDeps": [{"Name": "D2", "Version": "1.0"}],
            "RuntimeDeps": [{"Name": "D3", "Version": "1.0"}],
            "TestDeps": [{"Name": "D2", "Version": "1.0"}],
            "Logger": MockLog()
        }
        self.resolver = DependencyResolver(self.config_obj)

    def test_exception_on_package_downloader_exception(self):
        self.resolver.downloader.set_throws()
        self.assertRaises(DependencyResolverException, self.resolver.bfs)

    def test_exception_on_package_installer_exception(self):
        self.resolver.installer.set_throws()
        self.assertRaises(DependencyResolverException, self.resolver.bfs)

    @patch("modules.bootstrap.DependencyResolver.PackageInstaller", autospec=True)
    @patch("modules.bootstrap.DependencyResolver.PackageDownloader", autospec=True)
    def test_init_error_on_downloader_init(self, mock_package_downloader, mock_package_installers):
        mock_package_downloader.side_effect = PackageDownloaderException()
        mock_package_installers.side_effect = [MockPackageInstaller()]
        self.assertRaises(DependencyResolverException, DependencyResolver, self.config_obj)

    @patch("modules.bootstrap.DependencyResolver.PackageInstaller", autospec=True)
    @patch("modules.bootstrap.DependencyResolver.PackageDownloader", autospec=True)
    def test_init_error_on_installer_init(self, mock_package_downloader, mock_package_installers):
        mock_package_downloader.side_effect = [MockPackageDownloader()]
        mock_package_installers.side_effect = PackageInstallerException()
        self.assertRaises(DependencyResolverException, DependencyResolver, self.config_obj)

    @patch("modules.bootstrap.DependencyResolver.PackageInstaller", autospec=True)
    @patch("modules.bootstrap.DependencyResolver.PackageDownloader", autospec=True)
    def test_init_error_on_conf_init(self, mock_package_downloader, mock_package_installers):
        self.assertRaises(DependencyResolverException, DependencyResolver, {})
        self.assertRaises(DependencyResolverException, DependencyResolver, 10)
