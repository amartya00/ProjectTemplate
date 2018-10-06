import tempfile
import shutil
import os

from behave import given
from modules.workflow.Workflow import Workflow


@given("I have a C++ project with a proper md.json file.")
def i_have_a_cpp_project_with_a_proper_md_json_file(context):
    temp_dir = tempfile.TemporaryDirectory()
    context.temp_dir = temp_dir
    source_dir = os.path.join(os.path.dirname(__file__), "data")
    dest_dir = os.path.join(temp_dir.name, os.path.basename(source_dir))
    shutil.copytree(
        source_dir,
        dest_dir
    )
    context.data_dir = source_dir
    context.workflow = Workflow(project_root=dest_dir)


def after_feature(context):
    if hasattr(context, "temp_dir"):
        if os.path.isdir(context.temp_dir.name):
            context.temp_dir.cleanup()

