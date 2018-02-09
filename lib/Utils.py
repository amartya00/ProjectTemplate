import sys
import subprocess
import logging
from logging import handlers

sys.dont_write_bytecode = True


class Log:
    def __init__(self, config):
        self.log = logging.getLogger(config["ProgramName"])
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

    def get_logger(self):
        return self.log

    def info(self, msg):
        for l in msg.split("\n"):
            self.log.info(l)

    def error(self, msg):
        for l in msg.split("\n"):
            self.log.error(l)

    def warn(self, msg):
        for l in msg.split("\n"):
            self.log.warning(l)

    def debug(self, msg):
        for l in msg.split("\n"):
            self.log.debug(l)


def wget(url, dest):
    print(url)
    print(dest)
    p = subprocess.Popen(["wget", url, "-O", dest], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    err, out = p.communicate()
    exit_code = True
    if "ERROR" in out:
        err = out
        out = ""
        exit_code = False
    return err, out, exit_code
