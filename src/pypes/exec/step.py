import subprocess
from pathlib import Path
from typing import Dict, List

from jinja2 import Environment
from pypes.constants import default_pbs_context, header_template, qsub_template
from pypes.models.run import StepRun
from pypes.models.step import Step
from slugify import slugify


def build_depends_array(depends: List[str]):
    return "-W depend=afterok:{}".format(":".join(depends))


def run_pbs_step(
    step: Step,
    resources: Dict[str, Path],
    context: Dict[str, str],
    depends: List[str],
) -> str:
    command = Environment().from_string(step.command).render(**resources, **context)
    header_file_contents = (
        Environment()
        .from_string(header_template)
        .render(**context, **resources, command=command)
    )

    header_file_path = "{}.header.pbs".format(slugify(step.name, separator="_"))
    with open(header_file_path, "w+") as f:
        print("writing pbs header to {}".format(header_file_path))
        f.write(header_file_contents)

    process = subprocess.Popen(
        Environment()
        .from_string(qsub_template)
        .render(depends_str=build_depends_array(depends), header_file=header_file_path),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    process.wait()
    pbs_id = process.stdout.read().decode() if process.stdout else ""
    return pbs_id


def run_step(
    step: Step, resources: Dict[str, Path], context: Dict[str, str]
) -> StepRun:
    command_subbed = (
        Environment().from_string(step.command).render(**resources, **context)
    )
    process = subprocess.Popen(
        command_subbed, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    process.wait()
    stdout = process.stdout.read().decode() if process.stdout else ""
    stderr = process.stderr.read().decode() if process.stderr else ""
    returncode = process.returncode
    return StepRun(
        step_name=step.name,
        stdout=stdout,
        stderr=stderr,
        returncode=returncode,
        outcome="finished" if returncode == 0 else "error",
    )
