import os

from behave import given, when, then


@then("I should have the build folder.")
def i_should_have_the_build_folder(context):
    assert os.path.isdir(os.path.join(context.temp_dir.name, "data", "build"))


@then("It should contain a file called {file_name} .")
def it_should_contain_a_file(context, file_name):
    build_dir = os.path.join(context.temp_dir.name, "data", "build")
    assert os.path.isfile(os.path.join(build_dir, file_name))
