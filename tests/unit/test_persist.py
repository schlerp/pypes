from pathlib import Path
from typing import Callable

from pypes.models import Pipeline
from pypes.persist import (
    deserialise_pipeline,
    read_pipeline,
    serialise_pipeline,
    write_pipeline,
)


def test_config_serialise_deserialise(
    create_split_merge_pipeline: Callable[..., Pipeline]
):
    pipeline = create_split_merge_pipeline()
    serialised = serialise_pipeline(pipeline)
    deserialised = deserialise_pipeline(serialised)
    assert pipeline == deserialised


def test_persist_read_write(
    create_split_merge_pipeline: Callable[..., Pipeline],
    create_test_resource: Callable[..., Path],
):
    path = create_test_resource()
    pipeline = create_split_merge_pipeline()
    write_pipeline(pipeline, path)
    pipeline2 = read_pipeline(path)
    path.unlink()
    assert pipeline == pipeline2
