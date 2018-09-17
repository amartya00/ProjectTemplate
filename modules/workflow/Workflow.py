import os

from modules.config.Config import ConfigException, Config
from modules.build.CppCmake import BuildException, CppCmake
from modules.bootstrap.DependencyResolver import DependencyResolverException, DependencyResolver
from modules.package.Package import PackageException, Package


class WorkflowException (Exception):
    pass


class Workflow:
    STEPS = [
        "Bootstrap",
        "Build",
        "Test"
    ]

    def __init__(self, project_root=None):
        # Load config
        try:
            self.project_root = os.getcwd() if project_root is None else project_root
            self.config_obj = Config(self.project_root).get_config()
            self.logger = self.config_obj["Logger"]
        except ConfigException as e:
            raise WorkflowException("Could not configure project because " + str(e))

        # Detect build system
        build_system = self.config_obj["BuildSystem"]
        try:
            if build_system == "CppCmake":
                self.builder = CppCmake(self.config_obj)
            else:
                raise WorkflowException("Invalid build system: " + build_system)
        except BuildException as e:
            raise WorkflowException("Could not configure build because: " + str(e))

        # Initialize other stuff
        try:
            self.resolver = DependencyResolver(self.config_obj)
            self.package = Package(self.config_obj)
        except DependencyResolverException as e:
            raise WorkflowException("Could not initialize dependency resolver because: " + str(e))

    def execute_step(self, step_name):
        self.logger.info("Executing step: " + step_name + ".")
        try:
            if step_name == "Bootstrap":
                self.resolver.bfs()
            elif step_name == "Build":
                self.builder.build()
            elif step_name == "Test":
                self.builder.run_tests()
            elif step_name == "Clean":
                self.builder.clean()
            elif step_name == "Package":
                self.package.package()
            else:
                raise WorkflowException("Invalid step name.")
        except DependencyResolverException as e:
            raise WorkflowException("Could not resolve dependencies because: " + str(e))
        except BuildException as e:
            raise WorkflowException("Could not resolve build / test because: " + str(e))
        except PackageException as e:
            raise WorkflowException("Could not package because: " + str(e))
        self.logger.info("Finished executing step: " + step_name + ".")

    def run(self):
        for step in Workflow.STEPS:
            self.execute_step(step)



