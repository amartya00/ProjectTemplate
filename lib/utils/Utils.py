"""
Available utilities:
* trace_lib_deps
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import traceback
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


# Return synamically linked libraries
def ldd(libpath):
    libs = []
    p = subprocess.Popen(["ldd", libpath], stdout=subprocess.PIPE)
    o = p.communicate()[0].decode("UTF-8")
    for l in o.split("\n"):
        if l.strip() == "":
            continue
        else:
            temp = l.split("=>")
            if "vdso" in temp[0].strip():
                continue
            elif temp[0].strip().lower() == "statically linked":
                continue
            elif len(temp) == 2:
                libs.append((temp[0].split(" ")[0].strip(), temp[1].strip().split(" ")[0],
                             os.path.realpath(temp[1].strip().split(" ")[0])))
            else:
                libs.append((temp[0].split("/")[-1].split(" ")[0].strip(), temp[0].split(" ")[0].strip(),
                             os.path.realpath(temp[0].split(" ")[0].strip())))
    return libs


def recursiely_gather_libs(input_dict, library, logger):
    deps = ldd(library)
    for d in deps:
        if d[0] not in input_dict.keys():
            logger.info("[INFO] Gathering dependencies for: " + d[0])
            input_dict[d[0]] = {"ReferedFile": d[1], "ActualFile": d[2]}
            recursiely_gather_libs(input_dict, d[1], logger)


def get_system_dependencies(library, logger):
    deps = {}
    recursiely_gather_libs(deps, library, logger)


def recursive_file_search(root, fname):
    files = os.listdir(root)
    for f in files:
        if os.path.isfile(os.path.join(root, f)) and f == fname:
            return os.path.join(root, f)
        if os.path.isdir(os.path.join(root, f)):
            return recursive_file_search(os.path.join(root, f), fname)
    return None


def getopts(cmd_line_args, config):
    subcommands = ["trace_lib_deps"]
    logger = config.logger
    parser = argparse.ArgumentParser(prog="Utils", description=__doc__, usage="utils -c <subcommand> [options]",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f", "--libfile", help="Full path of the target library.")
    parser.add_argument("-c", "--subcommand", help="The subcommand.")
    args = parser.parse_args(cmd_line_args)

    sub_command = None
    lib_file = None

    if args.subcommand:
        sub_command = args.subcommand

    if args.libfile:
        lib_file = args.libfile

    if not sub_command:
        print("\n\n")
        print("Subcommand expected. Available subcommands are: " + str(subcommands))
        parser.print_help()
        print("\n\n")
        sys.exit(1)

    if sub_command == "trace_lib_deps":
        if not lib_file:
            print("Lib file required: ")
            parser.print_help()
            sys.exit(1)
        libs = {}
        try:
            recursiely_gather_libs(libs, lib_file, logger)
            print(json.dumps(libs, indent=4))
        except Exception as e:
            logger.error(str(e))
            logger.error("\nStacktrace:\n--------------------------------------")
            logger.error(traceback.format_exc())
            logger.error("--------------------------------------\n\n")
            sys.exit(1)
