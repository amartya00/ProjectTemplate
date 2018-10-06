from behave import when


@when("I run the c++ build workflow.")
def i_run_the_cpp_build_workflow(context):
    context.workflow.run()


@when("I run the packaging step.")
def i_run_the_packaging_step(context):
    context.workflow.execute_step("Package")
