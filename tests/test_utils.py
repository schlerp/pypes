import os
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple

from pypes.models import Pipeline, Step


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
            inputs={"a": create_test_resource("abc"), "b": create_test_resource("def")},
            outputs={"c": create_test_resource()},
            command="cat {{inputs['a']}} {{inputs['b']}} > {{outputs['c']}}",
        )
    return Step(name="should fail", command="false")


def cleanup_temp_files(steps: List[Step]) -> None:
    for step in steps:
        for path in step.inputs.values():
            delete_resource(path)
        for path in step.outputs.values():
            delete_resource(path)


def create_cp_step(name: str, source: Path, target: Path):
    return Step(
        name=name,
        inputs={"a": source},
        outputs={"b": target},
        command="cp {{ inputs['a'] }} {{ outputs['b'] }}",
    )


def create_merge_step(name: str, sources: Tuple[Path, Path], target: Path):
    return Step(
        name=name,
        inputs={"a": sources[0], "b": sources[1]},
        outputs={"c": target},
        command="cat {{ inputs['a'] }} {{ inputs['b'] }} > {{ outputs['c'] }}",
    )


def create_split_merge_pipeline(
    should_succeed: bool = True,
):
    res1 = create_test_resource("abc")
    res2 = create_test_resource()
    res3 = create_test_resource()
    resources = {"res1": res1, "res2": res2, "res3": res3}

    step1 = create_cp_step(name="step 1", source=res1, target=res2)
    step2 = create_cp_step(name="step 2", source=res1, target=res3)
    if should_succeed:
        res4 = create_test_resource()
        resources["res4"] = res4
        step3 = create_merge_step(name="step 3", sources=(res2, res3), target=res4)
    else:
        step3 = create_merge_step(name="step 3", sources=(res2, res3), target=res1)

    return Pipeline(
        name="test pipeline",
        owner="test",
        resources=resources,
        context={"test": "hello world!"},
        steps=[step1, step2, step3],
    )
