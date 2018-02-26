"""
For more help opn individual commands, please type project <command> --help.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")
sys.dont_write_bytecode = True

from lib.Config import Config
from lib.Build import Build

USAGE = "USAGE: project <command> <options>"
AVAILABLE_COMMANDS = ["build", "package", "help"]


def main():
    if len(sys.argv) < 2:
        print("\n\nERROR! Expecting a command")
        print(USAGE)
        print("\n\n")
        sys.exit(1)
    command = sys.argv[1]
    args = sys.argv[2:]
    config = Config()
    if command == "build":
        Build.getopts(args, config)
    elif command == "help":
        print("\n\n")
        print(__doc__)
        print(USAGE)
        print(AVAILABLE_COMMANDS)
        print("\n\n")
    else:
        print("\n\nERROR! Invalid command")
        print(USAGE)
        print(AVAILABLE_COMMANDS)
        print("\n\n")


if __name__ == "__main__":
    main()
