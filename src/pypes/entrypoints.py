from pathlib import Path
from typing import List, Dict
import hjson

import typer
from names_generator import generate_name

from pypes.cli.utils import add_resources, add_steps
from pypes.constants import DEFAULT_CONFIG_PATH
from pypes.models import Pipeline
from pypes.persist import read_pipeline, write_pipeline
from pypes.execution import run_pipeline

app = typer.Typer(name="pypes", help="Pypes: the unix pipeline builder!")


def get_name() -> str:
    return generate_name(style="capital")


@app.command("create")
def pipeline_create(
    name: str = typer.Option(
        default=get_name,
        prompt="Pipeline name",
        help="The name of the pipeline.",
    ),
    owner: str = typer.Option(
        default=get_name,
        prompt="Pipeline owner name",
        help="The name of the author of this pipeline (you).",
    ),
):
    pipeline = Pipeline(name=name, owner=owner)
    pipeline = add_resources(pipeline)
    pipeline = add_steps(pipeline)
    write_pipeline(pipeline)


@app.command("edit")
def pipeline_edit():
    typer.launch(DEFAULT_CONFIG_PATH)


@app.command("run")
def pipeline_run():
    pipeline = read_pipeline(Path("./.pipeline.conf"))
    exec_results = run_pipeline(pipeline)
    print(hjson.dumps(exec_results.dict(), indent=2, default=str))


def main():
    app()
