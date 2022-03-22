import os
from pathlib import Path

import hjson
import typer
from names_generator import generate_name

from pypes.cli.utils import build_pipeline_interactive, edit_pipeline_interactive
from pypes.execution import run_pipeline
from pypes.models import Pipeline
from pypes.persist import read_pipeline, write_pipeline

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
        default=os.environ.get("USER") or get_name,
        prompt="Pipeline owner name",
        help="The name of the author of this pipeline (you).",
    ),
):
    pipeline = Pipeline(name=name, owner=owner)
    pipeline = build_pipeline_interactive(pipeline)
    write_pipeline(pipeline)


@app.command("edit")
def pipeline_edit():
    pipeline = read_pipeline()
    pipeline = edit_pipeline_interactive(pipeline)
    write_pipeline(pipeline)


@app.command("run")
def pipeline_run():
    pipeline = read_pipeline()
    exec_results = run_pipeline(pipeline)
    print(hjson.dumps(exec_results.dict(), indent=2, default=str))


def main():
    app()
