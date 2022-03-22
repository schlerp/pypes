from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Callable, TypeVar, MutableMapping

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import clear
from pypes.cli.validators import (
    ChoiceValidator,
    KeyValidator,
    PathValidator,
    UniqueValidator,
    YesNoValidator,
)
from pypes.models import Pipeline, Step


T = TypeVar("T", Dict[Any, Any], List[Any])


def print_header(pipeline: Optional[Pipeline] = None):
    clear()
    print("Pypes: the unix workflow engine")
    print()
    if pipeline:
        print("╔" + ("═" * 63) + "╗")
        print("║ pipeline name:    {:43} ║".format(pipeline.name))
        print("║ pipeline owner:   {:43} ║".format(pipeline.owner))
        print(
            "║ pipeline created: {:43} ║".format(
                pipeline.created.strftime("%d-%m-%Y %H:%M")
            )
        )
        if pipeline.resources:
            print("╠" + ("═" * 63) + "╣")
            print("║ pipeline resources:" + (" " * 43) + "║")
            for k, v in pipeline.resources.items():
                print("║ * {:20} {:38} ║".format(k, str(v)))
        if pipeline.steps:
            print("╠" + ("═" * 63) + "╣")
            print("║ pipeline resources:" + (" " * 43) + "║")
            for s in pipeline.steps:
                print("║ * {:20} {:38} ║".format(s.name, s.command))
        print("╚" + ("═" * 63) + "╝")
        print()


def ask_finished(repeat_question: Optional[str] = None) -> bool:
    answer = prompt(
        repeat_question or "would you like to add another? (y/n)",
        default="yes",
        validator=YesNoValidator(),
    )
    if answer.strip().lower() in ["n", "no"]:
        return True
    return False


def while_not_finished_pipeline(
    pipeline: Pipeline,
    prompt_function: Callable[[Pipeline], Pipeline],
    repeat_question: Optional[str] = None,
):
    finished = False
    while not finished:
        print_header(pipeline)
        pipeline = prompt_function(pipeline)
        finished = ask_finished(repeat_question)
    return pipeline


def while_not_finished_mutateable(
    pipeline: Pipeline,
    prompt_function: Callable[[Pipeline, T, Any], T],
    mutatable: T,
    extra_context: Optional[Any] = None,
    repeat_question: Optional[str] = None,
):
    finished = False
    while not finished:
        print_header(pipeline)
        mutatable = prompt_function(pipeline, mutatable, extra_context)
        finished = ask_finished(repeat_question)
    return mutatable


def add_resources(pipeline: Pipeline):
    def add_resource_prompt(pipeline: Pipeline) -> Pipeline:
        path = prompt("Resource to add: ", validator=PathValidator(pipeline.resources))
        name = prompt(
            "Name for resource ({}): ".format(path),
            validator=UniqueValidator([x for x in pipeline.resources]),
        )
        pipeline.resources[name] = Path(path)
        return pipeline

    return while_not_finished_pipeline(
        pipeline,
        prompt_function=add_resource_prompt,
        repeat_question="Add another resource?",
    )


def choose_resource(
    resources: Dict[str, Path], prompt_message: str
) -> Tuple[str, Path]:
    resource_names = [x for x in resources.keys()]
    print_header()
    choice = prompt(
        prompt_message,
        validator=ChoiceValidator(resource_names),
        completer=WordCompleter(resource_names),
    )
    return choice, resources[choice]


def collect_resources(
    pipeline: Pipeline,
    prompt_message: str,
    exclude_keys: Optional[List[str]] = None,
) -> Dict[str, Path]:
    exclude_keys = exclude_keys or []

    def collect_resource_prompt(
        pipeline: Pipeline,
        collected_resources: Dict[str, Path],
        exclude_keys: List[str],
    ):
        name, path = choose_resource(
            {k: v for k, v in pipeline.resources.items() if k not in exclude_keys},
            prompt_message,
        )
        if name not in collected_resources:
            collected_resources[name] = path
        return collected_resources

    return while_not_finished_mutateable(
        pipeline, collect_resource_prompt, {}, exclude_keys
    )


def create_context(
    pipeline: Pipeline, context: Optional[Dict[str, str]] = None
) -> Dict[str, str]:
    context = context or {}

    def create_context_prompt(pipeline: Pipeline, context: Dict[str, str], *args):
        key = prompt(
            "Context key: ",
            validator=KeyValidator([x for x in context]),
        )
        value = prompt("Context value: ")
        context[key] = value
        return context

    return while_not_finished_mutateable(pipeline, create_context_prompt, {}, None)


def create_command(
    input_keys: Optional[List[str]] = None,
    output_keys: Optional[List[str]] = None,
    context_keys: Optional[List[str]] = None,
) -> str:
    print_header()
    input_keys = ["{{{{ inputs['{}'] }}}}".format(x) for x in input_keys or []]
    output_keys = ["{{{{ outputs['{}'] }}}}".format(x) for x in output_keys or []]
    context_keys = ["{{{{ context['{}'] }}}}".format(x) for x in context_keys or []]
    return prompt(
        "command: ",
        completer=WordCompleter(
            [*input_keys, *output_keys, *context_keys],
        ),
    )


def add_steps(pipeline: Pipeline):
    def add_step_prompt(pipeline: Pipeline) -> Pipeline:
        name = prompt(
            "Name of step: ",
            validator=UniqueValidator([x.name for x in pipeline.steps]),
        )
        inputs = collect_resources(pipeline, "input resource: ")
        outputs = collect_resources(
            pipeline, "output resource: ", exclude_keys=[x for x in inputs.keys()]
        )

        print_header(pipeline)
        print("add extra job context:")
        context = create_context(pipeline)

        print_header(pipeline)
        print("create the command:")
        command = create_command(
            [x for x in inputs.keys()],
            [x for x in outputs.keys()],
            [x for x in context.keys()],
        )

        pipeline.steps.append(
            Step(
                name=name,
                inputs=inputs,
                outputs=outputs,
                context=context,
                command=command,
            )
        )
        return pipeline

    return while_not_finished_pipeline(pipeline, add_step_prompt)
