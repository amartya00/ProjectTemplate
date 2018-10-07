import os
import json
import copy

from modules.config.Log import Log


class ConfigException (Exception):
    pass


class Config:
    ROOT = os.path.join(os.environ["HOME"], ".bob")
    CONFIG_FILE = os.path.join(os.environ["HOME"], ".bob", "config.json")

    DEFAULT_CONFIG = {
        "GlobalPackageCache": os.path.join(os.environ["HOME"], ".packagecache"),
        "LogFile": os.path.join(os.environ["HOME"], ".bob", "bob.log"),
        "Level": "INFO",
        "ProgramName": "Bob"
    }

    def __init__(self, project_root):
        # Read config file
        self.config = dict()
        if not os.path.isfile(Config.CONFIG_FILE):
            try:
                if not os.path.isdir(Config.ROOT):
                    os.makedirs(Config.ROOT)
                with open(Config.CONFIG_FILE, "w") as fp:
                    fp.write(json.dumps(Config.DEFAULT_CONFIG, indent=4))
                self.config = copy.deepcopy(Config.DEFAULT_CONFIG)
            except OSError as e:
                raise ConfigException("Failed to write new config file because " + str(e) + ".")
        else:
            self.config = copy.deepcopy(Config.DEFAULT_CONFIG)
            try:
                with open(Config.CONFIG_FILE, "r") as fp:
                    config = json.load(fp)
                    for key in config:
                        self.config[key] = config[key]
            except OSError as e:
                raise ConfigException("Could not read config file because " + str(e) + ".")
            except ValueError as e:
                with open(Config.CONFIG_FILE, "w") as fp:
                    fp.write(json.dumps(Config.DEFAULT_CONFIG, indent=4))
                self.config = copy.deepcopy(Config.DEFAULT_CONFIG)
        self.config["ProjectRoot"] = project_root
        self.config["BuildFolder"] = os.path.join(project_root, "build")

        # Read `md.json`
        try:
            if not os.path.isfile(os.path.join(project_root, "md.json")):
                raise ConfigException("Expecting a md.json file at project root.")
            with open(os.path.join(project_root, "md.json")) as fp:
                self.md = json.load(fp)
                if "Name" not in self.md:
                    raise ConfigException("\"Name\" parameter expected in md.json file.")
                if "Version" not in self.md:
                    raise ConfigException("\"Version\" parameter expected in md.json file.")
                if "BuildSystem" not in self.md:
                    raise ConfigException("\"BuildSystem\" parameter expected in md.json file.")
                for key in self.md:
                    self.config[key] = self.md[key]
        except OSError as e:
            raise ConfigException("Could not read md.json file because " + str(e) + ".")
        except ValueError as e:
            raise ConfigException("Malformed md.json file: " + str(e) + ".")
        self.logger = Log(self.config)
        self.config["Logger"] = self.logger
        self.config["LocalPackageCache"] = os.path.join(project_root, ".packagecache")
        self.config["BuildDir"] = os.path.join(project_root, "build")

    def get_config(self):
        return self.config



