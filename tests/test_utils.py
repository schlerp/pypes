import os
import tempfile
from pathlib import Path
from typing import List, Tuple

from pypes.models.pipeline import Pipeline
from pypes.models.step import Step


def delete_resource(path: Path) -> None:
    try:
        path.unlink()
    except:
        pass


def create_test_resource(content: str = "", exists: bool = True) -> Path:
    if not exists:
        return Path("i/hopefully/dont/exist")
    with tempfile.NamedTemporaryFile(delete=False) as f:
        if content:
            f.write(content.encode())
        return Path(f.name)


def create_test_step(
    should_succeed: bool = True,
) -> Step:
    if should_succeed:
        return Step(
            name="should succeed",
            inputs=[],
            outputs=[],
            command="echo 'Hello world!'",
        )
    return Step(name="should fail", command="false")


def create_cp_step(name: str, source: str, target: str) -> Step:
    return Step(
        name=name,
        inputs=[source],
        outputs=[target],
        command="cp {{{{ {} }}}} {{{{ {} }}}}".format(source, target),
    )


def create_merge_step(name: str, source1: str, source2: str, target: str) -> Step:
    return Step(
        name=name,
        inputs=[source1, source2],
        outputs=[target],
        command="cat {{{{ {} }}}} {{{{ {} }}}} > {{{{ {} }}}}".format(
            source1, source2, target
        ),
    )


def create_split_merge_pipeline(
    should_succeed: bool = True,
):
    res1 = create_test_resource("abc")
    res2 = create_test_resource()
    res3 = create_test_resource()
    resources = {"a": res1, "b": res2, "c": res3}

    step1 = create_cp_step(name="step 1", source="a", target="b")
    step2 = create_cp_step(name="step 2", source="a", target="c")
    if should_succeed:
        res4 = create_test_resource()
        resources["d"] = res4
        step3 = create_merge_step(name="step 3", source1="b", source2="c", target="d")
    else:
        step3 = create_merge_step(name="step 3", source1="b", source2="c", target="a")

    pipeline = Pipeline(
        name="test pipeline",
        owner="test",
        steps=[step1, step2, step3],
    )

    pipeline.add_resources(resources)

    return pipeline
