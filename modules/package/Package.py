import os

from modules.package.SnapPart import SnapPartException, SnapPart


class PackageException(Exception):
    pass


class Package:
    def __init__(self, config):
        self.config = config
        self.logger = config["Logger"]

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
            if package_type == "SnapPart":
                try:
                    # Add necessary parameters to step
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
                    snap_part = SnapPart(step)
                    snap_part.generate_snap_part()
                except SnapPartException as e:
                    raise PackageException(str(e))
                except KeyError as e:
                    raise PackageException("Invalid config : " + str(step) + " : " + str(e))
            else:
                raise PackageException("Invalid packaging type. Currently only supported are: SnapPart")


