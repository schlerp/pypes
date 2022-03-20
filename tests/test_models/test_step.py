from typing import Callable

from pypes.models import Step


def test_step_create(create_test_step: Callable[..., Step]):
    assert create_test_step() is not None


def test_step_run_success(
    create_test_step: Callable[..., Step], cleanup_temp_files: Callable[..., None]
):
    step = create_test_step()
    step.run()
    output_content = step.outputs[0].content
    cleanup_temp_files([step])
    assert output_content and output_content.decode() == "abcdef"


def test_step_run_failure(
    create_test_step: Callable[..., Step], cleanup_temp_files: Callable[..., None]
):
    step = create_test_step(should_succeed=False)
    step.run()
    cleanup_temp_files([step])
    assert step.status == "error"


def test_step_stdout():
    step = Step(
        name="test step",
        command="echo test",
    )
    step.run()
    assert step.stdout and step.stdout.strip() == "test"


def test_step_stderr():
    step = Step(
        name="test step",
        command=">&2 echo test",
    )
    step.run()
    assert step.stderr and step.stderr.strip() == "test"


def test_step_returncode():
    step = Step(
        name="test step",
        command="echo test",
    )
    step.run()
    assert step.returncode == 0
