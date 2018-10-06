import os
import tarfile
import json

from behave import then
from nose.tools import assert_equals, assert_true


@then("I should have the build folder.")
def i_should_have_the_build_folder(context):
    assert_true(os.path.isdir(os.path.join(context.temp_dir.name, "data", "build")))


@then("It should contain a file called {file_name} .")
def it_should_contain_a_file(context, file_name):
    build_dir = os.path.join(context.temp_dir.name, "data", "build")
    assert_true(os.path.isfile(os.path.join(build_dir, file_name)))


@then("the {file_name} should contain the following files.")
def the_file_name_should_contain_the_expected_files(context, file_name):
    all_files = []
    for row in context.table:
        all_files.extend([f.strip() for f in row])
    all_files.sort()
    build_dir = os.path.join(context.temp_dir.name, "data", "build")
    test_file = os.path.join(build_dir, file_name)
    with tarfile.open(test_file) as tfp:
        all_members = [e.name for e in tfp.getmembers()]
        all_members.sort()
        assert_equals(all_files, all_members)


@then("the md.json in the {file_name} should contain the following dependencies")
def the_md_json_in_the_file_name_should_contain_the_following_dependencies(context, file_name):
    dependencies = []
    for row in context.table:
        name, version = row
        name, version = name.strip(), version.strip()
        dependencies.append({"Name": name, "Version": version})
    dependencies.sort(key=lambda x: x["Name"])
    build_dir = os.path.join(context.temp_dir.name, "data", "build")
    test_file = os.path.join(build_dir, file_name)
    md_json_found = False
    with tarfile.open(test_file) as tfp:
        for f in tfp.getmembers():
            if f.name == "md.json":
                generated_dependencies = json.loads(tfp.extractfile(f).read().decode("utf-8"))["Dependencies"]
                generated_dependencies.sort(key=lambda x: x["Name"])
                assert_equals(dependencies, generated_dependencies)
                md_json_found = True
    assert_true(md_json_found)
