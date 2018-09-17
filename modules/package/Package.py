from modules.package.SnapPart import SnapPartException, SnapPart


class PackageException(Exception):
    pass


class Package:
    def __init__(self, config):
        self.config = config
        self.logger = config["Logger"]

    def package(self):
        # Run the packaging steps one by one
        if "Packaging" not in self.config:
            raise PackageException("Packaging information is not present in md.json.")
        for step in self.config["Packaging"]:
            if "Type" not in step:
                raise PackageException("Part type is needed. Otherwise I cannot tell what kind of package to produce.")
            package_type = step["Type"]
            if package_type == "SnapPart":
                try:
                    snap_part = SnapPart(step)
                    snap_part.generate_snap_part()
                except SnapPartException as e:
                    raise PackageException(str(e))
            else:
                raise PackageException("Invalid packaging type. Currently only supported are: SnapPart")


