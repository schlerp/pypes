import os
import tempfile
from typing import List, Tuple

from pypes.models import Pipeline, Resource, Step


def delete_resource(resource: Resource):
    if resource.exists:
        os.remove(resource.path)


def create_test_resource(content: str = "", exists: bool = True):
    if not exists:
        return Resource(path="i/hopefully/dont/exist")
    with tempfile.NamedTemporaryFile(delete=False) as f:
        if content:
            f.write(content.encode())
        return Resource(path=f.name)


def create_test_step(
    should_succeed: bool = True,
):
    if should_succeed:
        return Step(
            name="should succeed",
            inputs=[create_test_resource("abc"), create_test_resource("def")],
            outputs=[create_test_resource()],
            command="cat {inputs[0]} {inputs[1]} > {outputs[0]}",
        )
    return Step(name="should fail", command="false")


def cleanup_temp_files(steps: List[Step]):
    for step in steps:
        for r in step.inputs:
            delete_resource(r)
        for r in step.outputs:
            delete_resource(r)


def create_cp_step(name: str, source: Resource, target: Resource):
    return Step(
        id=name,
        name=name,
        inputs=[source],
        outputs=[target],
        command="cp {inputs[0]} {outputs[0]}",
    )


def create_merge_step(name: str, sources: Tuple[Resource, Resource], target: Resource):
    return Step(
        id=name,
        name=name,
        inputs=[*sources],
        outputs=[target],
        command="cat {inputs[0]} {inputs[1]} > {outputs[0]}",
    )


def create_split_merge_pipeline(
    should_succeed: bool = True,
):
    res1 = create_test_resource("abc")
    res2 = create_test_resource()
    res3 = create_test_resource()

    step1 = create_cp_step(name="step 1", source=res1, target=res2)
    step2 = create_cp_step(name="step 2", source=res1, target=res3)
    if should_succeed:
        res4 = create_test_resource()
        step3 = create_merge_step(name="step 3", sources=(res2, res3), target=res4)
    else:
        step3 = create_merge_step(name="step 3", sources=(res2, res3), target=res1)

    return Pipeline(
        name="test pipeline",
        owner="test",
        working_dir="/tmp",
        steps=[step1, step2, step3],
    )
