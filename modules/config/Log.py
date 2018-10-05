import logging
import sys
from logging import handlers


class LogException (Exception):
    pass


class Log:
    LEVEL_MAP = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARN": logging.WARN,
        "ERROR": logging.ERROR,
        "FATAL": logging.FATAL
    }

    def __init__(self, config):
        try:
            self.log = logging.getLogger(config["ProgramName"])
            self.config = config
            level = config["Level"]
            if level not in Log.LEVEL_MAP:
                raise LogException("Invalid log level: " + level + ". Allowed levels are: " + str(Log.LEVEL_MAP.keys()))
            self.log.setLevel(Log.LEVEL_MAP[level])
            fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            ch = logging.StreamHandler(sys.stdout)
            ch.setFormatter(fmt)
            self.log.addHandler(ch)
            fh = handlers.RotatingFileHandler(config["LogFile"], maxBytes=(1048576 * 5), backupCount=7)
            fh.setFormatter(fmt)
            self.log.addHandler(fh)
        except KeyError as e:
            raise LogException(str(e))

    @staticmethod
    def extract_msg(msg):
        try:
            return msg.decode("utf-8")
        except AttributeError:
            return str(msg)

    def info(self, msg):
        for l in Log.extract_msg(msg).split("\n"):
            self.log.info(l)

    def error(self, msg):
        for l in Log.extract_msg(msg).split("\n"):
            self.log.error(l)

    def warn(self, msg):
        for l in Log.extract_msg(msg).split("\n"):
            self.log.warning(l)

    def debug(self, msg):
        for l in Log.extract_msg(msg).split("\n"):
            self.log.debug(l)
