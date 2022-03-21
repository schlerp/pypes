import subprocess

from pypes.dag import get_execution_order, pipeline_to_dag
from pypes.models import Pipeline, PipelineRun, Step, StepRun


def run_step(step: Step) -> StepRun:
    command_subbed = step.command.format(
        inputs=step.inputs, outputs=step.outputs, context=step.context
    )
    process = subprocess.Popen(
        command_subbed, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    process.wait()
    stdout = process.stdout.read().decode() if process.stdout else ""
    stderr = process.stderr.read().decode() if process.stderr else ""
    returncode = process.returncode
    return StepRun(
        step_id=step.id,
        stdout=stdout,
        stderr=stderr,
        returncode=returncode,
        outcome="finished" if returncode == 0 else "error",
    )


def run_pipeline(pipeline: Pipeline) -> PipelineRun:
    pipeline_run = PipelineRun(pipeline_id=pipeline.id)
    dag = pipeline_to_dag(pipeline)
    step_runs = []
    errored = False
    for step_id in get_execution_order(dag):
        step = pipeline.get_step(step_id)
        step_run = run_step(step)
        step_runs.append(step_run)
        if step_run.returncode and step_run.returncode > 0:
            errored = True
            break
    pipeline_run.outcome = "error" if errored else "finished"
    pipeline_run.step_runs = step_runs
    return pipeline_run
