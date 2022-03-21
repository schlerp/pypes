from typing import Callable

from pypes.execution import run_step
from pypes.models import Step


def test_step_create(create_test_step: Callable[..., Step]):
    assert create_test_step() is not None


def test_step_run_success(
    create_test_step: Callable[..., Step], cleanup_temp_files: Callable[..., None]
):
    step = create_test_step()
    step_run = run_step(step)
    output_content = step.outputs[0].read()
    cleanup_temp_files([step])
    assert step_run.outcome == "finished" and output_content.decode() == "abcdef"


def test_step_run_failure(
    create_test_step: Callable[..., Step], cleanup_temp_files: Callable[..., None]
):
    step = create_test_step(should_succeed=False)
    step_run = run_step(step)
    cleanup_temp_files([step])
    assert step_run.outcome == "error"


def test_step_stdout(cleanup_temp_files: Callable[..., None]):
    step = Step(
        name="test step",
        command="echo test",
    )
    step_run = run_step(step)
    cleanup_temp_files([step])
    assert step_run.stdout.strip() == "test"


def test_step_stderr(cleanup_temp_files: Callable[..., None]):
    step = Step(
        name="test step",
        command=">&2 echo test",
    )
    step_run = run_step(step)
    cleanup_temp_files([step])
    assert step_run.stderr.strip() == "test"


def test_step_returncode(cleanup_temp_files: Callable[..., None]):
    step = Step(
        name="test step",
        command="echo test",
    )
    step_run = run_step(step)
    cleanup_temp_files([step])
    assert step_run.returncode == 0
