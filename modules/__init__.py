import sys
import os

sys.dont_write_bytecode = True
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")

from modules.workflow.Main import execute_cmd


def main():
    execute_cmd()
