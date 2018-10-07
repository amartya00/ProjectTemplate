from botocore.exceptions import ClientError

from modules.bootstrap.PackageDownloader import PackageDownloaderException
from modules.bootstrap.PackageInstaller import PackageInstallerException
from modules.bootstrap.DependencyResolver import DependencyResolverException
from modules.package.SnapPart import SnapPartException
from modules.build.CppCmake import BuildException
from modules.package.Package import PackageException


class MockLog:
    def __init__(self, config={}):
        self.config = config

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


class MockS3Client:
    def __init__(self):
        self.invocations = []
        self.raise_client_error = False

    def set_up_client_error(self):
        self.raise_client_error = True

    def download_fileobj(self, bucket, key, file_obj):
        if self.raise_client_error:
            raise ClientError(
                error_response={
                    "Error": {
                        "Code": "CLIENT_ERROR"
                    }
                },
                operation_name="download-fileobj"
            )
        self.invocations.append((bucket, key, file_obj))


class MockTarfilePointer:
    def __init__(self):
        self.invocations = {
            "extractall": [],
            "close": [],
            "add": []
        }
        self.exception = False

    def set_exception(self):
        self.exception = True

    def extractall(self, path):
        if self.exception:
            raise OSError("Error")
        self.invocations["extractall"].append(path)

    def add(self, filename, arcname=None):
        self.invocations["add"].append((filename, arcname))

    def close(self):
        if self.exception:
            raise OSError("Error")
        self.invocations["close"].append(None)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class MockFilePointer:
    def __init__(self, read_text=""):
        self.read_text = read_text
        self.invocations = {
            "read": [],
            "write": []
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def read(self):
        self.invocations["read"].append(None)
        return self.read_text

    def write(self, write_text):
        self.invocations["write"].append(write_text)


class MockPackageDownloader:
    def __init__(self):
        self.invocations = []
        self.throws = False

    def set_throws(self):
        self.throws = True

    def unset_throws(self):
        self.throws = False

    def download_and_extract(self, package_list):
        if self.throws:
            raise PackageDownloaderException()
        self.invocations.append(package_list[:])


class MockPackageInstaller:
    def __init__(self, collected_dependencies=[]):
        self.collected_dependencies = collected_dependencies
        self.invocations = []
        self.invocation_count = -1
        self.throws = False

    def set_throws(self):
        self.throws = True

    def unset_throws(self):
        self.throws = False

    def install_packages(self, package_list):
        if self.throws:
            raise PackageInstallerException()
        self.invocations.append(package_list[:])
        self.invocation_count = self.invocation_count + 1
        return self.collected_dependencies[self.invocation_count]


class MockConfig:
    def __init__(self, config={}):
        self.config=config

    def get_config(self):
        return self.config


class MockBuildSystem:
    def __init__(self):
        self.invocations = {
            "Test": 0,
            "Build": 0,
            "Clean": 0
        }
        self.build_throws = False
        self.test_throws = False

    def set_build_throws(self):
        self.build_throws = True

    def set_test_throws(self):
        self.test_throws = True

    def unset_build_throws(self):
        self.build_throws = False

    def unset_test_throws(self):
        self.test_throws = False

    def build(self):
        if self.build_throws:
            raise BuildException()
        self.invocations["Build"] = self.invocations["Build"] + 1

    def run_tests(self):
        if self.test_throws:
            raise BuildException()
        self.invocations["Test"] = self.invocations["Test"] + 1

    def clean(self):
        self.invocations["Clean"] = self.invocations["Clean"] + 1


class MockDependencyResolver:
    def __init__(self):
        self.invocations = 0
        self.throws = False

    def set_throws(self):
        self.throws = True

    def unset_throws(self):
        self.throws = False

    def bfs(self):
        if self.throws:
            raise DependencyResolverException()
        self.invocations = self.invocations + 1


class MockTemporaryFilePointer:
    def __init__(self, name):
        self.name = name
        self.invocations = {
            "write": [],
            "flush": 0
        }

    def write(self, text):
        self.invocations["write"].append(text)

    def flush(self):
        self.invocations["flush"] = self.invocations["flush"] + 1

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class MockSnapPart:
    def __init__(self, conf={}):
        self.conf = conf
        self.throws = False

    def set_throws(self):
        self.throws = True

    def unset_throws(self):
        self.throws = False

    def generate_snap_part(self):
        if self.throws:
            raise SnapPartException()


class MockPackage:
    def __init__(self):
        self.invocations = 0
        self.throws = False

    def set_throws(self):
        self.throws = True

    def unset_throws(self):
        self.throws = False

    def package(self):
        self.invocations = self.invocations + 1
        if self.throws:
            raise PackageException()


class MockLogger:
    def __init__(self):
        self.handlers = []
        self.level = None
        self.infos = list()
        self.debugs = []
        self.warns = []
        self.errors = []

    def addHandler(self, handler):
        self.handlers.append(handler)

    def setLevel(self, level):
        self.level = level

    def info(self, msg):
        self.infos.append(msg)

    def debug(self, msg):
        self.debugs.append(msg)

    def warning(self, msg):
        self.warns.append(msg)

    def error(self, msg):
        self.errors.append(msg)


class MockWorkflow:
    def __init__(self):
        self.invocations = {
            "Run": [],
            "Step": []
        }

    def execute_step(self, step_name):
        self.invocations["Step"].append(step_name)

    def run(self):
        self.invocations["Run"].append(None)


class MockTemporaryDirectory:
    def __init__(self, folder_name: "str"):
        self.name = folder_name

    def __enter__(self):
        return self.name

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class MockSnapCMake:
    def __init__(self):
        self.invocations = 0
        self.throws = False

    def package(self):
        self.invocations = self.invocations + 1

    def set_throws(self):
        self.throws = True

    def unset_throws(self):
        self.throws = False
