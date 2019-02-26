"""
This is a build system. This can:
1. Bootstrap dependencies
2. Build the project
3. Run tests

You can run the end to end workflow or a single step. The available steps are:
1. Build
2. Test
3. Clean
"""

import argparse
import sys

from modules.workflow.Workflow import WorkflowException, Workflow


def execute_cmd():
    version_maj = sys.version_info[0]
    version_min = sys.version_info[1]
    if version_maj < 3:
        print("\n\n[ERROR] Need python 3 to run. Your version: " + str(version_maj) + "." + str(version_min))
        sys.exit(1)
    parser = argparse.ArgumentParser(prog="Bob", description=__doc__, usage="bob [options]",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-c", "--clean", help="Clean the project.", action="store_true")
    parser.add_argument("-s", "--step", help="Run single step.")

    args = parser.parse_args(sys.argv[1:])

    try:
        workflow = Workflow()
        if args.clean:
            workflow.execute_step("Clean")
            return True
        if args.step:
            workflow.execute_step(args.step)
            return True
        workflow.run()
    except WorkflowException as e:
        print("\n\n[ERROR] Error occured " + str(e))
