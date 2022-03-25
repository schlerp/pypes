import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar

from prompt_toolkit import prompt
from prompt_toolkit.completion import FuzzyWordCompleter
from prompt_toolkit.shortcuts import clear
from pypes.cli.completers import FilePathCompleter
from pypes.cli.validators import (
    ChoiceValidator,
    KeyValidator,
    PathValidator,
    UniqueValidator,
    YesNoValidator,
)
from pypes.models.pipeline import Pipeline
from pypes.models.step import Step

T = TypeVar("T", Dict[Any, Any], List[Any])


def truncate_text(text: str, max_len: int) -> str:
    return text if len(text) < (max_len - 3) else "{}...".format(text[0 : max_len - 3])


def print_header(pipeline: Optional[Pipeline] = None):
    clear()
    print("Pypes: the unix workflow engine")
    print()
    if pipeline:
        print("╔" + ("═" * 53) + "╗")
        print("║ pipeline name:    {:33} ║".format(pipeline.name))
        print("║ pipeline owner:   {:33} ║".format(pipeline.owner))
        print(
            "║ pipeline created: {:33} ║".format(
                pipeline.created.strftime("%d-%m-%Y %H:%M")
            )
        )
        if pipeline.resources:
            print("╠" + ("═" * 53) + "╣")
            print("║ pipeline resources:" + (" " * 33) + "║")
            for name, path in pipeline.resources.items():
                print(
                    "║ - {:20} {:28} ║".format(
                        truncate_text(name, 20), truncate_text(str(path), 28)
                    )
                )
        if pipeline.context:
            print("╠" + ("═" * 53) + "╣")
            print("║ pipeline context:" + (" " * 35) + "║")
            for key, value in pipeline.context.items():
                print(
                    "║ - {:20} {:28} ║".format(
                        truncate_text(key, 20), truncate_text(value, 28)
                    )
                )
        if pipeline.steps:
            print("╠" + ("═" * 53) + "╣")
            print("║ pipeline steps:" + (" " * 37) + "║")
            for s in pipeline.steps:
                print(
                    "║ - {:20} {:28} ║".format(
                        truncate_text(s.name, 20), truncate_text(s.command, 28)
                    )
                )
        print("╚" + ("═" * 53) + "╝")
        print()


def ask_yesno(question: str) -> bool:
    answer = prompt(
        question,
        validator=YesNoValidator(),
        completer=FuzzyWordCompleter(["yes", "no"]),
    )
    if answer.strip().lower() in ["n", "no"]:
        return False
    return True


def while_not_finished_pipeline(
    pipeline: Pipeline,
    prompt_function: Callable[[Pipeline], Pipeline],
    question: str,
):
    finished = False
    while not finished:
        print_header(pipeline)
        pipeline = prompt_function(pipeline)
        finished = not ask_yesno(question)
    return pipeline


def while_not_finished_mutateable(
    pipeline: Pipeline,
    prompt_function: Callable[[Pipeline, T, Any], T],
    mutatable: T,
    question: str,
    extra_context: Optional[Any] = None,
):
    finished = False
    while not finished:
        print_header(pipeline)
        mutatable = prompt_function(pipeline, mutatable, extra_context)
        finished = not ask_yesno(question)
    return mutatable


def add_resources(pipeline: Pipeline):
    def add_resource_prompt(pipeline: Pipeline) -> Pipeline:
        path = prompt(
            "Path of resource: ",
            validator=PathValidator(pipeline.resources),
            completer=FilePathCompleter(),
            complete_while_typing=True,
        )
        name = prompt(
            "Name of resource: ",
            default=os.path.splitext(os.path.split(path)[-1])[0],
            validator=UniqueValidator([x for x in pipeline.resources]),
        )
        pipeline.resources[name] = Path(path)
        return pipeline

    return while_not_finished_pipeline(
        pipeline,
        prompt_function=add_resource_prompt,
        question="Add another resource? (yes/no) ",
    )


def choose_resource(
    resources: Dict[str, Path], prompt_message: str
) -> Tuple[str, Path]:
    resource_names = [x for x in resources.keys()]
    choice = prompt(
        prompt_message,
        validator=ChoiceValidator(resource_names),
        completer=FuzzyWordCompleter(resource_names),
    )
    return choice, resources[choice]


def collect_resources(
    pipeline: Pipeline,
    prompt_message: str,
    exclude_keys: Optional[List[str]] = None,
) -> List[str]:
    exclude_keys = exclude_keys or []

    def collect_resource_prompt(
        pipeline: Pipeline,
        collected_resources: List[str],
        exclude_keys: List[str],
    ):
        name, path = choose_resource(
            {k: v for k, v in pipeline.resources.items() if k not in exclude_keys},
            prompt_message,
        )
        if name not in collected_resources:
            collected_resources.append(name)
        return collected_resources

    return while_not_finished_mutateable(
        pipeline,
        collect_resource_prompt,
        [],
        "Use another resource? (y/n) ",
        exclude_keys,
    )


def create_command(pipeline: Pipeline, keys: List[str]) -> str:
    print_header(pipeline)
    keys_formatted = ["{{{{ {} }}}}".format(x) for x in keys or []]
    return prompt(
        "comand for this step:\n",
        completer=FuzzyWordCompleter(keys_formatted),
    )


def add_context(pipeline: Pipeline) -> Pipeline:
    def create_context_prompt(
        pipeline: Pipeline, context: Dict[str, str], *args
    ) -> Dict[str, str]:
        key = prompt(
            "Context key: ",
            validator=KeyValidator([x for x in context]),
        )
        value = prompt("Context value: ")
        context[key] = value
        return context

    pipeline.context = while_not_finished_mutateable(
        pipeline,
        create_context_prompt,
        pipeline.context,
        "Add more key/vals to context? (y/n) ",
    )
    return pipeline


def add_steps(pipeline: Pipeline):
    def add_step_prompt(pipeline: Pipeline) -> Pipeline:
        name = prompt(
            "Name of step: ",
            validator=UniqueValidator([x.name for x in pipeline.steps]),
        )
        inputs = collect_resources(pipeline, "input resource: ")
        outputs = collect_resources(pipeline, "output resource: ", exclude_keys=inputs)

        command = create_command(
            pipeline,
            [x for x in inputs]
            + [x for x in outputs]
            + [x for x in pipeline.context.keys()],
        )

        pipeline.steps.append(
            Step(
                name=name,
                inputs=inputs,
                outputs=outputs,
                command=command,
            )
        )
        return pipeline

    return while_not_finished_pipeline(
        pipeline, add_step_prompt, "Add another step to pipeline? (y/n) "
    )


def build_pipeline_interactive(pipeline: Pipeline) -> Pipeline:
    if ask_yesno("Would you like to add resources? (y/n) "):
        pipeline = add_resources(pipeline)
    if ask_yesno("Would you like to add extra context? (y/n) "):
        pipeline = add_context(pipeline)
    if ask_yesno("Would you like to add steps? (y/n) "):
        pipeline = add_steps(pipeline)
    return pipeline


def edit_pipeline_interactive(pipeline: Pipeline) -> Pipeline:
    # TODO: implement editing logic
    print_header(pipeline)
    return pipeline
