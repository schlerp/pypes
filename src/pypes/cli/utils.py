import re
from pathlib import Path
from typing import Dict, Optional, List, Tuple

from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import clear
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import ValidationError, Validator
from pypes.models import Pipeline, Step


class PathValidator(Validator):
    def __init__(self, resources: Optional[Dict[str, Path]] = None):
        self.resources = resources or {}

    def validate(self, document):
        regex_pattern = r"^(/)?([^/\0]+(/)?)+$"
        if not re.match(regex_pattern, document.text):
            raise ValidationError(message="input is not path like!")
        elif document.text in self.resources.values():
            raise ValidationError(message="resource is already added!")


class KeyValidator(Validator):
    def __init__(self, existing_keys: Optional[List[str]] = None):
        self.existing_keys = existing_keys or []

    def validate(self, document):
        regex_pattern = r"^[a-zA-Z0-9_]*$"
        if not re.match(regex_pattern, document.text):
            raise ValidationError(message="input is not a valid key (no spaces)!")
        elif document.text in self.existing_keys:
            raise ValidationError(
                message="key {} already in use!".format(document.text)
            )


class UniqueValidator(Validator):
    def __init__(self, unique_list: Optional[List[str]] = None):
        self.unique_list = unique_list or []

    def validate(self, document):
        if document.text in self.unique_list:
            raise ValidationError(message="{} is already in use!".format(document.text))


class YesNoValidator(Validator):
    def validate(self, document):
        text = document.text.strip().lower()
        if text not in ["yes", "no", "y", "n"]:
            raise ValidationError(message="{} is not one of yes/no!".format(text))


class ChoiceValidator(Validator):
    def __init__(self, unique_list: Optional[List[str]] = None):
        self.unique_list = unique_list or []

    def validate(self, document):
        if document.text not in self.unique_list:
            raise ValidationError(
                message="{} is not a valid choice!".format(document.text)
            )


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


def add_resources(pipeline: Pipeline):
    finished = False
    while not finished:
        print_header(pipeline)
        print("current resources:")
        print(
            "\n".join(
                ["  * {}: {}".format(k, v) for k, v in pipeline.resources.items()]
            )
        )
        path = prompt("Resource to add: ", validator=PathValidator(pipeline.resources))
        name = prompt(
            "Name for resource ({}): ".format(path),
            validator=UniqueValidator([x for x in pipeline.resources]),
        )
        pipeline.resources[name] = Path(path)
        answer = prompt(
            "would you like to add another? (y/n) ", validator=YesNoValidator()
        )
        if answer.strip().lower() in ["n", "no"]:
            finished = True
    return pipeline


def choose_resource(resources: Dict[str, Path]) -> Tuple[str, Path]:
    print("resources:")
    print("\n".join(["  * {}: {}".format(k, v) for k, v in resources.items()]))
    resource_names = [x for x in resources.keys()]
    choice = prompt(
        "choose a resource: ",
        validator=ChoiceValidator(resource_names),
        completer=WordCompleter(resource_names),
    )
    return choice, resources[choice]


def collect_resources(
    pipeline: Pipeline, exclude_keys: Optional[List[str]] = None
) -> Dict[str, Path]:
    exclude_keys = exclude_keys or []
    collected_resources: Dict[str, Path] = {}
    finished_inputs = False
    while not finished_inputs:
        name, path = choose_resource(
            {k: v for k, v in pipeline.resources.items() if k not in exclude_keys}
        )
        if name not in collected_resources:
            collected_resources[name] = path
        answer = prompt(
            "would you like to add another resource? (y/n) ",
            validator=YesNoValidator(),
        )
        if answer.strip().lower() in ["n", "no"]:
            finished_inputs = True
    return collected_resources


def create_context(context: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    ret_dict = context or {}
    finished = False
    while not finished:
        print("current context:")
        print("\n".join(["  * {}: {}".format(k, v) for k, v in ret_dict.items()]))
        key = prompt(
            "Context key (alphanumeric with no spaces): ",
            validator=KeyValidator([x for x in ret_dict]),
        )
        value = prompt("Context value: ")
        ret_dict[key] = value
        answer = prompt(
            "would you like to add another resource? (y/n) ",
            validator=YesNoValidator(),
        )
        if answer.strip().lower() in ["n", "no"]:
            finished = True
    return ret_dict


def create_command(
    input_keys: Optional[List[str]] = None,
    output_keys: Optional[List[str]] = None,
    context_keys: Optional[List[str]] = None,
) -> str:
    clear()
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
    finished = False
    while not finished:
        print_header(pipeline)
        print("current steps:")
        print("\n".join(["  * {}".format(s.name) for s in pipeline.steps]))
        name = prompt(
            "Name of step: ",
            validator=UniqueValidator([x.name for x in pipeline.steps]),
        )

        print_header(pipeline)
        print("select input resources:")
        inputs = collect_resources(pipeline)
        print_header(pipeline)
        print("select output resources:")
        outputs = collect_resources(pipeline, exclude_keys=[x for x in inputs.keys()])

        print_header(pipeline)
        print("add extra job context:")
        context = create_context()

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

        answer = prompt(
            "would you like to add another step? (y/n) ", validator=YesNoValidator()
        )
        if answer.strip().lower() in ["n", "no"]:
            finished = True
    return pipeline
