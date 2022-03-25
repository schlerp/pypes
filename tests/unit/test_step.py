from typing import Callable

from pypes.exec.step import run_step
from pypes.models.step import Step


def test_step_create(create_test_step: Callable[..., Step]):
    assert create_test_step() is not None


def test_step_run_success(create_test_step: Callable[..., Step]):
    step = create_test_step()
    step_run = run_step(step, {}, {})
    output_content = step_run.stdout.strip().lower()
    assert step_run.outcome == "finished" and output_content == "hello world!"


def test_step_run_failure(create_test_step: Callable[..., Step]):
    step = create_test_step(should_succeed=False)
    step_run = run_step(step, {}, {})
    assert step_run.outcome == "error"


def test_step_stdout():
    step = Step(
        name="test step",
        command="echo test",
    )
    step_run = run_step(step, {}, {})
    assert step_run.stdout.strip() == "test"


def test_step_stderr():
    step = Step(
        name="test step",
        command=">&2 echo test",
    )
    step_run = run_step(step, {}, {})
    assert step_run.stderr.strip() == "test"


def test_step_returncode():
    step = Step(
        name="test step",
        command="echo test",
    )
    step_run = run_step(step, {}, {})
    assert step_run.returncode == 0
