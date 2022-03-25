from typing import Dict, List

from pypes.exec.depend import get_ancestors, get_execution_order, pipeline_to_dag
from pypes.exec.step import run_pbs_step, run_step
from pypes.models.guards import is_pbs_step
from pypes.models.pipeline import Pipeline
from pypes.models.run import PipelineRun, StepRun


def run_pipeline(pipeline: Pipeline) -> PipelineRun:
    pipeline_run = PipelineRun(pipeline=pipeline)
    dag = pipeline_to_dag(pipeline)
    step_runs = []
    errored = False
    for step_id in get_execution_order(dag):
        step = pipeline.get_step(step_id)
        step_run = run_step(step, pipeline.resources, pipeline.context)
        step_runs.append(step_run)
        if step_run.returncode and step_run.returncode > 0:
            errored = True
            break
    pipeline_run.outcome = "error" if errored else "finished"
    pipeline_run.step_runs = step_runs
    return pipeline_run


def run_pbs_pipeline(pipeline: Pipeline) -> PipelineRun:
    pipeline_run = PipelineRun(pipeline=pipeline)
    dag = pipeline_to_dag(pipeline)
    step_runs: List[StepRun] = []
    step_to_pbs_id_map: Dict[str, str] = {}
    errored = False
    for step_id in get_execution_order(dag):
        print("running step: {}".format(step_id))
        step = pipeline.get_step(step_id)
        pbs_depends = [step_to_pbs_id_map[x] for x in get_ancestors(dag, step_id)]
        pbs_id = run_pbs_step(
            step,
            pipeline.resources,
            pipeline.context,
            depends=pbs_depends,
        )
        step_to_pbs_id_map[step_id] = pbs_id
    pipeline_run.outcome = "error" if errored else "finished"
    pipeline_run.step_runs = step_runs
    return pipeline_run
