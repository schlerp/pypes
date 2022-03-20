import os
import tempfile
from typing import List

from pypes.models import Resource, Step


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


def create_test_step(should_succeed: bool = True):
    if should_succeed:
        return Step(
            name="should succeed",
            status="queued",
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
