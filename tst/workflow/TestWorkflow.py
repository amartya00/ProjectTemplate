import unittest

from unittest.mock import patch
from tst.testutils.Mocks import MockConfig, MockLog, MockBuildSystem, MockDependencyResolver, MockPackage

from modules.config.Config import ConfigException
from modules.build.CppCmake import BuildException
from modules.bootstrap.DependencyResolver import DependencyResolverException
from modules.workflow.Workflow import WorkflowException, Workflow


class TestWorkflow (unittest.TestCase):
    @patch("modules.workflow.Workflow.Package", autospec=True)
    @patch("modules.workflow.Workflow.DependencyResolver", autospec=True)
    @patch("modules.workflow.Workflow.CppCmake", autospec=True)
    @patch("modules.workflow.Workflow.Config", autospec=True)
    @patch("os.getcwd", return_value="CWD")
    def test_workflow_happy_case(self, mock_getcwd, mock_config, mock_build_system, mock_dependency_resolver, mock_pkg):
        config = {
            "Logger": MockLog(),
            "BuildSystem": "CppCmake"
        }
        mock_config.side_effect = [MockConfig(config)]

        builder = MockBuildSystem()
        mock_build_system.side_effect = [builder]

        resolver = MockDependencyResolver()
        mock_dependency_resolver.side_effect = [resolver]

        package = MockPackage()
        mock_pkg.side_effect = [package]

        w = Workflow()
        w.run()

        self.assertEqual(1, resolver.invocations)
        self.assertEqual(1, builder.invocations["Build"])
        self.assertEqual(1, builder.invocations["Test"])
        self.assertEqual(0, builder.invocations["Clean"])
        self.assertEqual(0, package.invocations)

    @patch("modules.workflow.Workflow.DependencyResolver", autospec=True)
    @patch("modules.workflow.Workflow.CppCmake", autospec=True)
    @patch("modules.workflow.Workflow.Config", autospec=True)
    @patch("os.getcwd", return_value="CWD")
    def test_exception_on_bad_build_system(self, mock_getcwd, mock_config, mock_build_system, mock_dependency_resolver):
        config = {
            "Logger": MockLog(),
            "BuildSystem": "Clown"
        }
        mock_config.side_effect = [MockConfig(config)]

        builder = MockBuildSystem()
        mock_build_system.side_effect = [builder]

        resolver = MockDependencyResolver()
        mock_dependency_resolver.side_effect = [resolver]

        self.assertRaises(WorkflowException, Workflow)

    @patch("modules.workflow.Workflow.Package", autospec=True)
    @patch("modules.workflow.Workflow.DependencyResolver", autospec=True)
    @patch("modules.workflow.Workflow.CppCmake", autospec=True)
    @patch("modules.workflow.Workflow.Config", autospec=True)
    @patch("os.getcwd", return_value="CWD")
    def test_single_step_happy_case(self, mock_getcwd, mock_config, mock_build_system, mock_dependency_resolver, mock_pkg):
        config = {
            "Logger": MockLog(),
            "BuildSystem": "CppCmake"
        }
        mock_config.side_effect = [MockConfig(config)]

        builder = MockBuildSystem()
        mock_build_system.side_effect = [builder]

        resolver = MockDependencyResolver()
        mock_dependency_resolver.side_effect = [resolver]
        package = MockPackage()
        mock_pkg.side_effect = [package]

        w = Workflow()
        w.execute_step("Bootstrap")
        self.assertEqual(1, resolver.invocations)
        self.assertEqual(0, builder.invocations["Build"])
        self.assertEqual(0, builder.invocations["Test"])
        self.assertEqual(0, builder.invocations["Clean"])
        self.assertEqual(0, package.invocations)

        w.execute_step("Build")
        self.assertEqual(1, resolver.invocations)
        self.assertEqual(1, builder.invocations["Build"])
        self.assertEqual(0, builder.invocations["Test"])
        self.assertEqual(0, builder.invocations["Clean"])
        self.assertEqual(0, package.invocations)

        w.execute_step("Test")
        self.assertEqual(1, resolver.invocations)
        self.assertEqual(1, builder.invocations["Build"])
        self.assertEqual(1, builder.invocations["Test"])
        self.assertEqual(0, builder.invocations["Clean"])
        self.assertEqual(0, package.invocations)

        w.execute_step("Clean")
        self.assertEqual(1, resolver.invocations)
        self.assertEqual(1, builder.invocations["Build"])
        self.assertEqual(1, builder.invocations["Test"])
        self.assertEqual(1, builder.invocations["Clean"])
        self.assertEqual(0, package.invocations)

        w.execute_step("Package")
        self.assertEqual(1, resolver.invocations)
        self.assertEqual(1, builder.invocations["Build"])
        self.assertEqual(1, builder.invocations["Test"])
        self.assertEqual(1, builder.invocations["Clean"])
        self.assertEqual(1, package.invocations)

        self.assertRaises(WorkflowException, w.execute_step, "BogusStep")

    @patch("modules.workflow.Workflow.Config", autospec=True)
    @patch("os.getcwd", return_value="CWD")
    def test_init_exception_on_config_exception(self, mock_getcwd, mock_config):
        mock_config.side_effect = ConfigException()
        self.assertRaises(WorkflowException, Workflow)

    @patch("modules.workflow.Workflow.CppCmake", autospec=True)
    @patch("modules.workflow.Workflow.Config", autospec=True)
    @patch("os.getcwd", return_value="CWD")
    def test_init_exception_on_build_exception(self, mock_getcwd, mock_config, mock_build_system):
        config = {
            "Logger": MockLog(),
            "BuildSystem": "CppCmake"
        }
        mock_config.side_effect = [MockConfig(config)]
        mock_build_system.side_effect = BuildException()

        self.assertRaises(WorkflowException, Workflow)

    @patch("modules.workflow.Workflow.DependencyResolver", autospec=True)
    @patch("modules.workflow.Workflow.CppCmake", autospec=True)
    @patch("modules.workflow.Workflow.Config", autospec=True)
    @patch("os.getcwd", return_value="CWD")
    def test_init_exception_on_resolver_exception(self, mock_getcwd, mock_config, mock_build_system, mock_dependency_resolver):
        config = {
            "Logger": MockLog(),
            "BuildSystem": "CppCmake"
        }
        mock_config.side_effect = [MockConfig(config)]

        builder = MockBuildSystem()
        mock_build_system.side_effect = [builder]
        mock_dependency_resolver.side_effect = DependencyResolverException()

        self.assertRaises(WorkflowException, Workflow)

    @patch("modules.workflow.Workflow.Package", autospec=True)
    @patch("modules.workflow.Workflow.DependencyResolver", autospec=True)
    @patch("modules.workflow.Workflow.CppCmake", autospec=True)
    @patch("modules.workflow.Workflow.Config", autospec=True)
    @patch("os.getcwd", return_value="CWD")
    def test_exception_on_step_exception(self, mock_getcwd, mock_config, mock_build_system, mock_dependency_resolver, mock_pkg):
        config = {
            "Logger": MockLog(),
            "BuildSystem": "CppCmake"
        }
        mock_config.side_effect = [MockConfig(config)]

        builder = MockBuildSystem()
        mock_build_system.side_effect = [builder]

        resolver = MockDependencyResolver()
        mock_dependency_resolver.side_effect = [resolver]

        package = MockPackage()
        mock_pkg.side_effect = [package]

        w = Workflow()

        resolver.set_throws()
        self.assertRaises(WorkflowException, w.run)
        resolver.unset_throws()

        builder.set_build_throws()
        self.assertRaises(WorkflowException, w.run)
        builder.unset_build_throws()

        builder.set_test_throws()
        self.assertRaises(WorkflowException, w.run)
        builder.unset_test_throws()

        package.set_throws()
        self.assertRaises(WorkflowException, w.execute_step, "Package")
        package.unset_throws()



