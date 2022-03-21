from typing import Callable

from pypes.exceptions import NoMatchingStepException
from pypes.models import Pipeline, Step


def test_create_pipeline():
    pipeline = Pipeline(
        name="test pipeline", owner="test", working_dir="/tmp", steps=[]
    )
    assert pipeline.name == "test pipeline"


def test_pipeline_get_step_succeed(create_test_step: Callable[..., Step]):
    step = create_test_step()
    pipeline = Pipeline(
        name="test pipeline", owner="test", working_dir="/tmp", steps=[step]
    )
    assert pipeline.get_step(step.id) is not None


def test_pipeline_get_step_failure(
    create_test_step: Callable[..., Step], cleanup_temp_files: Callable[..., None]
):
    step = create_test_step()
    pipeline = Pipeline(
        name="test pipeline", owner="test", working_dir="/tmp", steps=[step]
    )
    try:
        pipeline.get_step("i dont exist")
        assert False
    except NoMatchingStepException:
        assert True
    finally:
        cleanup_temp_files(pipeline.steps)
