from pathlib import Path
from typing import Callable

from pypes.exec.pipeline import run_pipeline
from pypes.models.pipeline import Pipeline
from pypes.models.step import Step


def test_run_pipeline_succeed(create_test_step: Callable[..., Step]):
    step = create_test_step()
    pipeline = Pipeline(name="test pipeline", owner="test", steps=[step])
    run = run_pipeline(pipeline)
    assert run.outcome == "finished"


def test_run_pipeline_failure(create_test_step: Callable[..., Step]):
    step = create_test_step(should_succeed=False)
    pipeline = Pipeline(name="test pipeline", owner="test", steps=[step])
    run = run_pipeline(pipeline)
    assert run.outcome == "error"


def test_run_pipeline_merge_succeed(
    create_test_resource: Callable[..., Path],
    create_split_merge_pipeline: Callable[..., Pipeline],
):
    pipeline = create_split_merge_pipeline()
    run = run_pipeline(pipeline)
    assert pipeline.resources["d"].read_text().strip() == "abcabc"
