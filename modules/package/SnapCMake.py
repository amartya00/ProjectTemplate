"""
This module is responsible for creating a snap package with CMake plugin.
This needs a lot of parameters:
1. Snapcraft parameters (refer to https://docs.snapcraft.io/build-snaps/syntax for detailed documentation):
  1.1 Version
  1.2 Summary
  1.3 Grade
  1.4 Confinement
  1.5 Apps

2. Dependencies
"""
import os
import tempfile
import shutil
import subprocess


class SnapCMakeException(Exception):
    pass


class SnapCMake:
    def __init__(self, config):
        self.config = config
        self.logger = config["Logger"]

    def generate_dependencies(self):
        dependencies = []
        # NOTE: We need only build and test dependencies for making a snap
        if "Dependencies" in self.config:
            dependencies.extend(self.config["Dependencies"])
        if "RuntimeDeps" in self.config:
            dependencies.extend(self.config["RuntimeDeps"])
        return dependencies

    def get_package_path(self, package_name: "str", package_version: "str"):
        try:
            local_path = os.path.join(
                self.config["GlobalPackageCache"],
                package_name, package_version,
                package_name + ".tar")
            if not os.path.isfile(local_path):
                raise SnapCMakeException("Package " + package_name + "/" + package_version + " not bootstrapped.")
            return local_path
        except KeyError as e:
            raise SnapCMakeException("Missing configuration: " + str(e))

    def generate_snappy_yaml(self):
        self.logger.info("Creating snappy yaml.")
        # Package metadata
        yaml_str = "name: " + self.config["Name"] + "\n"
        yaml_str = yaml_str + "version: " + "'" + self.config["Version"] + "'\n"
        yaml_str = yaml_str + "summary: " + self.config["Summary"] + "\n"
        yaml_str = yaml_str + "grade: " + self.config["Grade"] + "\n"
        yaml_str = yaml_str + "confinement: " + self.config["Confinement"] + "\n"
        yaml_str = yaml_str + "description: " + self.config["Description"] + "\n\n"
        yaml_str = yaml_str + "apps:\n"
        for a in self.config["Apps"]:
            yaml_str = yaml_str + "  " + a["Name"] + ":\n"
            yaml_str = yaml_str + "    command: " + a["Command"] + "\n\n"

        # Dependencies
        yaml_str = yaml_str + "parts:\n"
        for d in self.generate_dependencies():
            package_name = d["Name"]
            package_version = d["Version"]
            yaml_str = yaml_str + "  " + package_name + ":\n"
            # Plugin will always be cmake
            yaml_str = yaml_str + "    plugin: cmake\n"
            yaml_str = yaml_str + "    source: " + self.get_package_path(
                package_name,
                package_version) + "\n\n"
        yaml_str = yaml_str + "  " + self.config["Name"] + ":\n"
        yaml_str = yaml_str + "    plugin: cmake\n"
        yaml_str = yaml_str + "    source: " + self.config["ProjectRoot"] + "\n"
        yaml_str = yaml_str + "    configflags: [-DPACKAGE_CACHE=" + self.config["LocalPackageCache"] + "]\n\n"
        self.logger.info(yaml_str)
        return yaml_str

    def package(self):
        self.logger.info("Building snap.")
        snappy_text = self.generate_snappy_yaml()
        with tempfile.TemporaryDirectory() as temp_folder:
            snap_folder = os.path.join(temp_folder, "snap")
            os.makedirs(snap_folder)
            with open(os.path.join(snap_folder, "snapcraft.yaml"), "w") as fp:
                fp.write(snappy_text)
                self.logger.info("Created snapcraft.yaml in temporary folder: " + snap_folder)
            cwd = os.getcwd()
            os.chdir(temp_folder)
            try:
                p = subprocess.Popen(["snapcraft"])
                o, e = p.communicate()
            except OSError as e:
                raise SnapCMakeException("You might not have snapcraft installed. Error message: " + str(e))
            if not p.returncode == 0:
                self.logger.error("Building snap failed.")
                self.logger.error(e)
                raise SnapCMakeException("Failed to build the snap.")
            else:
                self.logger.info("Built snap in folder: " + temp_folder)
                for s in os.listdir(temp_folder):
                    if s.endswith(".snap"):
                        shutil.copyfile(os.path.join(temp_folder, s), os.path.join(self.config["BuildFolder"], s))
                        self.logger.info("Copied the snap to: " + os.path.join(self.config["BuildFolder"], s))
                        self.logger.info("Finshed snap building process.")
            os.chdir(cwd)
            self.logger.info("Done building snap.")
        return self

