import json
import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")
sys.dont_write_bytecode = True

from lib.utils.Utils import Log


class ConfigException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class Config:
    PROGRAM_NAME = "project helper"
    DEFAULT_CONF_FOLDER = os.path.join(os.environ["HOME"], ".projects")
    DEFAULT_CONF_FILE = os.path.join(DEFAULT_CONF_FOLDER, "config.json")
    DEFAULT_CONF = {
        "PackageCacheRoot": os.path.join(DEFAULT_CONF_FOLDER, "packageceche"),
        "BucketName": "amartya00-service-artifacts",
        "ProgramName": PROGRAM_NAME,
        "Level": "DEBUG",
        "LogFile": os.path.join(DEFAULT_CONF_FOLDER, "project.log")
    }

    @staticmethod
    def first_run():
        is_first_run = False
        if not os.path.isdir(Config.DEFAULT_CONF_FOLDER):
            os.makedirs(Config.DEFAULT_CONF_FOLDER)
            is_first_run = True
        if not os.path.isfile(Config.DEFAULT_CONF_FILE):
            is_first_run = True
            with open(Config.DEFAULT_CONF_FILE, "w") as fp:
                fp.write(json.dumps(Config.DEFAULT_CONF, indent=4))
        return is_first_run

    def __init__(self, conf_file_path=None):
        is_first_run = Config.first_run()
        self.conf_file_path = os.path.join(Config.DEFAULT_CONF_FILE) if not conf_file_path else conf_file_path
        self.conf = dict(Config.DEFAULT_CONF)
        try:
            override = json.loads(open(self.conf_file_path, "r").read())
            for key in override.keys():
                self.conf[key] = override[key]
            self.logger = Log(self.conf)
        except IOError as e:
            self.logger = Log(self.conf)
            self.logger.error("Error while reading config file " + self.conf_file_path + " : " + str(e))
            raise ConfigException("Error while reading config file " + self.conf_file_path + " : " + str(e))
        if is_first_run:
            self.logger.info("Creating project folder " + Config.DEFAULT_CONF_FOLDER)
            self.logger.info("Creating config file " + Config.DEFAULT_CONF_FILE)

    def add_conf_params(self, extra_params):
        for param in extra_params.keys():
            self.conf[param] = extra_params[param]
        return self
