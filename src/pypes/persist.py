from pathlib import Path

from hjson import dumps, loads

from pypes.models import Pipeline


class InvalidConfigFileException(Exception):
    pass


def deserialise_pipeline(pipeline_text: str) -> Pipeline:
    pipeline = Pipeline(**loads(pipeline_text))
    return Pipeline(
        name=pipeline.name,
        owner=pipeline.owner,
        steps=pipeline.steps,
        working_dir=pipeline.working_dir,
        created=pipeline.created,
    )


def serialise_pipeline(pipeline: Pipeline):
    return dumps(pipeline.dict(), indent=2, default=str)


def read_pipeline(path: Path) -> Pipeline:
    return deserialise_pipeline(path.read_text())


def write_pipeline(pipeline: Pipeline, path: Path = Path("./.pipeline.conf")):
    path.rename(path.with_suffix(".bak"))
    try:
        config_text = serialise_pipeline(pipeline)
        with open(path, "w") as f:
            f.write(config_text)
    except Exception as e:
        path.with_suffix(".bak").rename(path)
        raise e
