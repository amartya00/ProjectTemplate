import unittest
import sys

from unittest.mock import patch, call
from modules.workflow.Main import execute_cmd
from tst.testutils.Mocks import MockWorkflow


class TestMain (unittest.TestCase):
    @patch.object(sys, "argv", ["bob"])
    @patch("modules.workflow.Main.Workflow", autospec=True)
    def test_start_workflow_full(self, mock_workflow):
        w = MockWorkflow()
        mock_workflow.side_effect = [w]
        execute_cmd()
        self.assertEquals(1, len(w.invocations["Run"]))

    @patch.object(sys, "argv", ["bob", "-s", "MyStep"])
    @patch("modules.workflow.Main.Workflow", autospec=True)
    def test_workflow_step(self, mock_workflow):
        w = MockWorkflow()
        mock_workflow.side_effect = [w]
        execute_cmd()
        self.assertEquals(0, len(w.invocations["Run"]))
        self.assertEquals(["MyStep"], w.invocations["Step"])

    @patch.object(sys, "argv", ["bob", "-c"])
    @patch("modules.workflow.Main.Workflow", autospec=True)
    def test_workflow_clean(self, mock_workflow):
        w = MockWorkflow()
        mock_workflow.side_effect = [w]
        execute_cmd()
        self.assertEquals(0, len(w.invocations["Run"]))
        self.assertEquals(["Clean"], w.invocations["Step"])

