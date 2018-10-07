import os

from modules.package.SnapPart import SnapPartException, SnapPart
from modules.package.SnapCMake import SnapCMakeException, SnapCMake


class PackageException(Exception):
    pass


class Package:
    def __init__(self, config):
        self.config = config
        self.logger = config["Logger"]

    def add_params_to_step(self, step):
        try:
            step["Logger"] = self.logger
            step["ProjectRoot"] = self.config["ProjectRoot"]
            step["BuildFolder"] = self.config["BuildFolder"]
            step["LocalPackageCache"] = self.config["LocalPackageCache"]
            if "Dependencies" in self.config:
                step["Dependencies"] = self.config["Dependencies"]
            if "RuntimeDeps" in self.config:
                step["RuntimeDeps"] = self.config["RuntimeDeps"]
            if "BuildDeps" in self.config:
                step["BuildDeps"] = self.config["BuildDeps"]
            if "TestDeps" in self.config:
                step["TestDeps"] = self.config["TestDeps"]
        except KeyError as e:
            raise(PackageException("Missing parameter needed fo packaging steps: " + str(e)))

    def package(self):
        # Check for the build folder
        if "BuildFolder" not in self.config:
            raise PackageException("Malformed config in package: Expecting a \"BuildConfig\" in config.")
        if not os.path.isdir(self.config["BuildFolder"]):
            raise PackageException("Project not built yet. Please build first.")
        # Run the packaging steps one by one
        if "Packaging" not in self.config:
            raise PackageException("Packaging information is not present in md.json.")
        for step in self.config["Packaging"]:
            if "Type" not in step:
                raise PackageException("Part type is needed. Otherwise I cannot tell what kind of package to produce.")
            package_type = step["Type"]
            # Add necessary parameters to step
            self.add_params_to_step(step)

            # Handle snap part
            if package_type == "SnapPart":
                try:
                    snap_part = SnapPart(step)
                    snap_part.generate_snap_part()
                except SnapPartException as e:
                    raise PackageException(str(e))
            # Handle snap cmake
            elif package_type == "SnapCMake":
                try:
                    snap_cmake = SnapCMake(step)
                    snap_cmake.package()
                except SnapCMakeException as e:
                    raise PackageException(str(e))
            else:
                raise PackageException("Invalid packaging type. Currently only supported are: SnapPart")


