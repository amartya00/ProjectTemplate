"""
Bunch of utility functions
"""

import os


class Utils:
    @staticmethod
    def debug(message):
        if "DEBUG_MODE" in os.environ.keys() and os.environ["DEBUG_MODE"] == "true":
            print("[DEBUG] " + message)

    @staticmethod
    def info(message):
        print("[INFO] " + message)

    @staticmethod
    def error(message):
        print("[ERROR] " + message)

    @staticmethod
    def warn(message):
        print("[WARNING] " + message)
