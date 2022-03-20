from typing import Callable

from pypes.models import Pipeline, Step


def test_create_pipeline():
    pipeline = Pipeline(
        name="test pipeline", owner="test", working_dir="/tmp", steps=[]
    )
    assert pipeline.status == "queued"


def test_run_pipeline_succeed(create_test_step: Callable[..., Step]):
    step = create_test_step()
    pipeline = Pipeline(
        name="test pipeline", owner="test", working_dir="/tmp", steps=[step]
    )
    pipeline.run()
    assert pipeline.status == "finished"


def test_run_pipeline_failure(create_test_step: Callable[..., Step]):
    step = create_test_step(should_succeed=False)
    pipeline = Pipeline(
        name="test pipeline", owner="test", working_dir="/tmp", steps=[step]
    )
    try:
        pipeline.run()
    except:
        pass
    assert pipeline.status == "error"
