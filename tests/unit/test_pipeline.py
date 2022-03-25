from pathlib import Path
from typing import Callable

from pypes.exceptions import KeyAlreadyInUseException, NoMatchingStepException
from pypes.models.pipeline import Pipeline
from pypes.models.step import Step


def test_create_pipeline():
    pipeline = Pipeline(name="test pipeline", owner="test", steps=[])
    assert pipeline.name == "test pipeline"


def test_pipeline_get_step_succeed(create_test_step: Callable[..., Step]):
    step = create_test_step()
    pipeline = Pipeline(name="test pipeline", owner="test", steps=[step])
    assert pipeline.get_step(step.name) is not None


def test_pipeline_add_resource_succeed():
    pipeline = Pipeline(name="test pipeline", owner="test")
    pipeline.add_resources({"test": Path(".")})
    assert True


def test_pipeline_add_resource_failure():
    pipeline = Pipeline(name="test pipeline", owner="test")
    try:
        pipeline.add_resources({"test": Path(".")})
        pipeline.add_resources({"test": Path(".")})
        assert False
    except KeyAlreadyInUseException:
        assert True


def test_pipeline_add_context_succeed():
    pipeline = Pipeline(name="test pipeline", owner="test")
    pipeline.add_context({"test": "test"})
    assert True


def test_pipeline_add_context_failure():
    pipeline = Pipeline(name="test pipeline", owner="test")
    try:
        pipeline.add_context({"test": "test"})
        pipeline.add_context({"test": "test"})
        assert False
    except KeyAlreadyInUseException:
        assert True


def test_pipeline_get_step_failure(create_test_step: Callable[..., Step]):
    step = create_test_step()
    pipeline = Pipeline(name="test pipeline", owner="test", steps=[step])
    try:
        pipeline.get_step("i dont exist")
        assert False
    except NoMatchingStepException:
        assert True
