"""
This module computes and downloads and installs the entire dependency graph of a project (using BFS).
It makes use of package downloader and installer to bootstrap the project.
"""

from modules.bootstrap.PackageInstaller import PackageInstallerException, PackageInstaller
from modules.bootstrap.PackageDownloader import PackageDownloaderException, PackageDownloader


class DependencyResolverException (Exception):
    pass


class DependencyResolver:
    def __init__(self, config_obj):
        try:
            self.config_obj = config_obj
            self.downloader = PackageDownloader(self.config_obj)
            self.installer = PackageInstaller(self.config_obj)
            self.logger = self.config_obj["Logger"]
        except PackageDownloaderException as e:
            raise DependencyResolverException(str(e))
        except PackageInstallerException as e:
            raise DependencyResolverException(str(e))
        except KeyError as e:
            raise DependencyResolverException(str(e))
        except TypeError as e:
            raise DependencyResolverException(str(e))

    def gather_initial_deps(self):
        dependencies = {}
        if "Dependencies" in self.config_obj:
            for dependency in self.config_obj["Dependencies"]:
                dependencies[dependency["Name"]] = dependency

        if "RuntimeDeps" in self.config_obj:
            for dependency in self.config_obj["RuntimeDeps"]:
                dependencies[dependency["Name"]] = dependency

        if "TestDeps" in self.config_obj:
            for dependency in self.config_obj["TestDeps"]:
                dependencies[dependency["Name"]] = dependency

        if "BuildDeps" in self.config_obj:
            for dependency in self.config_obj["BuildDeps"]:
                dependencies[dependency["Name"]] = dependency

        return list(dependencies.values())

    def bfs(self):
        try:
            next_frontier = self.gather_initial_deps()
            visited = {}
            for dep in next_frontier:
                visited[str(dep)] = dep
            while len(next_frontier) > 0:
                frontier = next_frontier
                next_frontier = []
                self.downloader.download_and_extract(frontier)
                neighbours = self.installer.install_packages(frontier).values()
                for n in list(neighbours):
                    if str(n) not in visited:
                        visited[str(n)] = n
                        next_frontier.append(n)
            # TODO: Save the dependency closure in a file to be used during packaging
            return list(visited.values())
        except PackageDownloaderException as e:
            raise DependencyResolverException(str(e))
        except PackageInstallerException as e:
            raise DependencyResolverException(str(e))
