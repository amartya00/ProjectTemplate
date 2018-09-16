import logging
import sys
from logging import handlers


class Log:
    def __init__(self, config):
        self.log = logging.getLogger(config["ProgramName"])
        self.config = config
        if config["Level"] == "DEBUG":
            self.log.setLevel(logging.DEBUG)
        elif config["Level"] == "INFO":
            self.log.setLevel(logging.INFO)
        elif config["Level"] == "WARN":
            self.log.setLevel(logging.WARN)
        else:
            self.log.setLevel(logging.FATAL)
        fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(fmt)
        self.log.addHandler(ch)
        fh = handlers.RotatingFileHandler(config["LogFile"], maxBytes=(1048576 * 5), backupCount=7)
        fh.setFormatter(fmt)
        self.log.addHandler(fh)

    @staticmethod
    def extract_msg(msg):
        try:
            return msg.decode("utf-8")
        except:
            return str(msg)

    def get_logger(self):
        return self.log

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

    def __str__(self):
        return "Logger for " + self.config["LogFile"]
