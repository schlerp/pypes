from pathlib import Path

from hjson import dumps, loads

from pypes.models import Pipeline
from pypes.constants import DEFAULT_CONFIG_PATH


class InvalidConfigFileException(Exception):
    pass


def deserialise_pipeline(pipeline_text: str) -> Pipeline:
    pipeline = Pipeline(**loads(pipeline_text))
    return pipeline


def serialise_pipeline(pipeline: Pipeline) -> str:
    return dumps(pipeline.dict(), indent=2, default=str)


def read_pipeline(path: Path = Path(DEFAULT_CONFIG_PATH)) -> Pipeline:
    return deserialise_pipeline(path.read_text())


def write_pipeline(pipeline: Pipeline, path: Path = Path("./.pipeline.conf")):
    if path.exists():
        path.rename(path.with_suffix(".bak"))
    try:
        config_text = serialise_pipeline(pipeline)
        with open(path, "w") as f:
            f.write(config_text)
        if path.with_suffix(".bak").exists():
            path.with_suffix(".bak").unlink()
    except Exception as e:  # pragma: no cover
        if path.with_suffix(".bak").exists():
            path.with_suffix(".bak").rename(path)
        raise e
