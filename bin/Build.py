import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")
sys.dont_write_bytecode = True

from lib.PackageDownloader import PackageDownloaderException, PackageDownloader
from lib.PackageInstaller import PackageInstallerException, PackageInstaller
from lib.DependencyResolver import DependencyResolverException, DependencyResolver
from lib.Utils import Log


def main():
    main_config = {
        "PackageCacheRoot": os.path.join(os.environ["HOME"], ".packagecache"),
        "BucketName": "amartya00-service-artifacts"
    }
    logger_config = {
        "ProgramName": "TEST",
        "Level": "DEBUG",
        "LogFile": "/home/amartya/Log.log"
    }
    log = Log(logger_config)
    d = PackageDownloader(config=main_config, logger=log)
    i = PackageInstaller(config=main_config, logger=log)
    r = DependencyResolver(config=main_config, logger=log)
    try:
        #d.clear_cache([("sex", "0.0"), ("auth", "0.1"), ("auth", "0.0")]).get_package("auth", "0.0")
        #i.install("auth", "0.0")
        r.bfs("auth", "0.0")
    except PackageDownloaderException as e:
        print(str(e))
    except PackageInstallerException as e:
        print(str(e))


if __name__ == "__main__":
    main()