from unittest.mock import Mock


class MockPackageInstaller:
    def __init__(self, config, logger, package_map):
        self.package_map = package_map

    def install(self, package_name, package_version):
        pass

    def get_installed_md(self, package_name, package_version):
        return self.package_map[(package_name,package_version)]


class MockPackageDownloader:
    def __init__(self, config, logger):
        pass

    def prep_folders(self):
        pass

    def download_package(self, package_name, package_version):
        pass

    def extract_package(self, package_name, package_version):
        pass

    def get_package(self, package_name, package_version):
        print(package_name)
        print(package_version)
        pass

    def clear_cache(self, package_list):
        pass


class MockLog:
    def __init__(self):
        pass

    def get_logger(self):
        pass

    def info(self, msg):
        pass

    def error(self, msg):
        pass

    def warn(self, msg):
        pass

    def debug(self, msg):
        pass