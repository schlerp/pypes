from prompt_toolkit.validation import ValidationError, Validator
from typing import Dict, Optional, List
from pathlib import Path
import re


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
