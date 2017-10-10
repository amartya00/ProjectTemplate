"""
Utility to build / test a cmake package.
This downloads and bootstraps the dependencies too.
"""

import os
import sys
import argparse

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")
from libs.Build import Builder, BuilderException
from libs.Utils import Utils


def getopts(cmdlineargs):
    parser = argparse.ArgumentParser(prog="BuildProject", description=__doc__, usage="BuildProject [options]",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-t", "--runtests", help="Enable this option to run the tests as well.", action = "store_true")
    parser.add_argument("-c", "--clean", help="Clean the package cache.", action = "store_true")
    parser.add_argument("-b", "--build_only", help="Just run make in the build folder. This skips dependency resolution and running cmake.", action = "store_true")
    args = parser.parse_args(cmdlineargs)

    runtests = False
    clean = False
    build_only = False

    if args.runtests:
        runtests = True

    if args.clean:
        clean =True

    if args.build_only:
        build_only = True

    try:
        b = Builder()
        if clean:
            b.clean()
        elif build_only:
            b.make()
        else:
            b.resolve_dependencies().symlink_bootstrapped_libs().run_cmake().make()
            if runtests:
                b.run_tests()
    except BuilderException as e:
        Utils.error(str(e))
        return False
    return True


