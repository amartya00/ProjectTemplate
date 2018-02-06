import os
import sys
import json

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")
sys.dont_write_bytecode = True

from lib.PackageDownloader import PackageDownloaderException, PackageDownloader
from lib.PackageInstaller import PackageInstallerException, PackageInstaller


class DependencyResolverException (Exception):
    def __init__(self, message = "Unknown exception."):
        self.message = message

    def __str__(self):
        return self.message


class DependencyResolver:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.cwd = os.getcwd()
        if not os.path.isfile(os.path.join(self.cwd, "md.json")):
            self.logger.error("Expected to find md.json file in CWD. Not there!")
            raise DependencyResolverException("Expected md.json file in $CWD.")
        self.md = json.loads(open("md.json", "r").read())
        self.dependency_list = []

    def s3_url(self, package_name, package_version):
        key = package_name + "/" + package_version + "/" + package_name + ".tar"
        return "https://s3.amazonaws.com/" + self.config["BucketName"] + "/" + key

    @staticmethod
    def extract_deps(md):
        deps = []
        if "BuildDeps" in md:
            deps.extend(md["BuildDeps"])
        if "RuntimeDeps" in md:
            deps.extend(md["RuntimeDeps"])
        if "TestDeps" in md:
            deps.extend(md["TestDeps"])
        if "Dependencies" in md:
            deps.extend(md["Dependencies"])
        return deps

    def bfs(self):
        package_name = self.md["Package"]
        package_version = self.md["Version"]
        self.logger.info("Resolving dependencies.")
        downloader = PackageDownloader(self.config, self.logger)
        installer = PackageInstaller(self.config, self.logger)
        next_frontier = DependencyResolver.extract_deps(self.md)
        visited = [
            {"Package": package_name, "Version": package_version}
        ]
        while not len(next_frontier) == 0:
            frontier = next_frontier
            next_frontier = []
            for dep in frontier:
                if dep not in visited:
                    visited.append(dep)
                    pkg_name = dep["Package"]
                    pkg_version = dep["Version"]
                    self.logger.info(pkg_name + "/" + pkg_version + " is a dependency.")
                    downloader.get_package(pkg_name, pkg_version)
                    installer.install(pkg_name, pkg_version)
                    deps = DependencyResolver.extract_deps(
                        installer.get_installed_md(pkg_name, pkg_version))
                    next_frontier.extend(deps)
        self.logger.info("Resolved dependencies.")
        return self
