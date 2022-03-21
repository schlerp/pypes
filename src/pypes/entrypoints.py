import typer
from names_generator import generate_name

from pypes.constants import DEFAULT_CONFIG_PATH

app = typer.Typer(name="pypes", help="Pypes: the unix pipeline builder!")


def get_name() -> str:
    return generate_name(style="capital")


@app.command("create")
def create_pipeline(
    name: str = typer.Option(
        default=get_name,
        prompt="Pipeline Name",
        help="The name of this pipeline.",
    ),
    author: str = typer.Option(
        default=get_name,
        prompt="Your name",
        help="The name of the author of this pipeline (you).",
    ),
    working_dir: str = typer.Option(
        default=".", help="The root directory for this pipeline."
    ),
):
    print(working_dir)
    print(name)
    print(author)


@app.command("edit")
def edit_pipeline():
    typer.launch(DEFAULT_CONFIG_PATH)


def main():
    app()
