import sys

sys.dont_write_bytecode = True


class MockPackageInstaller:
    def __init__(self, config, logger, package_map):
        self.package_map = package_map
        self.invocations = {
            "install": [],
            "get_installed_md": []
        }

    def install(self, package_name, package_version):
        self.invocations["install"].append((package_name, package_version))
        pass

    def get_installed_md(self, package_name, package_version):
        self.invocations["get_installed_md"].append((package_name, package_version))
        return self.package_map[(package_name, package_version)]


class MockPackageDownloader:
    def __init__(self, config, logger):
        self.invocations = {
            "get_package": [],
            "download_package": [],
            "extract_package": [],
            "clear_cache": [],
            "prep_folders": []
        }

    def prep_folders(self):
        pass

    def download_package(self, package_name, package_version):
        pass

    def extract_package(self, package_name, package_version):
        pass

    def get_package(self, package_name, package_version):
        self.invocations["get_package"].append((package_name, package_version))
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


class MockTarfilePointer:
    def __init__(self):
        self.invocations = {
            "extractall": [],
            "close": []
        }

    def extractall(self, path):
        self.invocations["extractall"].append(path)

    def close(self):
        self.invocations["close"].append(None)


class MockProcess:
    def __init__(self, out, err, exit_code):
        self.out = out
        self.err = err
        self.returncode = exit_code
        self.invocations = {
            "communicate": []
        }

    def communicate(self):
        return self.out, self.err


class MockFilePointer:
    def __init__(self, read_text):
        self.read_text = read_text
        self.invocations = {
            "read": [],
            "write": []
        }

    def read(self):
        self.invocations["read"].append(None)
        return self.read_text

    def write(self, write_text):
        self.invocations["write"].append(write_text)


class MockDependencyResolver:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.invocations = {
            "bfs": []
        }

    def s3_url(self, package_name, package_version):
        return None

    @staticmethod
    def extract_deps(md):
        return None

    def bfs(self):
        self.invocations["bfs"].append(None)
        return self

