from typing import Callable

from pypes.execution import run_pipeline
from pypes.models import Pipeline, Step


def test_run_pipeline_succeed(
    create_test_step: Callable[..., Step], cleanup_temp_files: Callable[..., None]
):
    step = create_test_step()
    pipeline = Pipeline(
        name="test pipeline", owner="test", working_dir="/tmp", steps=[step]
    )
    run = run_pipeline(pipeline)
    cleanup_temp_files(pipeline.steps)
    assert run.outcome == "finished"


def test_run_pipeline_failure(
    create_test_step: Callable[..., Step], cleanup_temp_files: Callable[..., None]
):
    step = create_test_step(should_succeed=False)
    pipeline = Pipeline(
        name="test pipeline", owner="test", working_dir="/tmp", steps=[step]
    )
    run = run_pipeline(pipeline)
    cleanup_temp_files(pipeline.steps)
    assert run.outcome == "error"
