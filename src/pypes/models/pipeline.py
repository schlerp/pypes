from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from pydantic import Field
from pypes.constants import default_pbs_context
from pypes.exceptions import KeyAlreadyInUseException, NoMatchingStepException
from pypes.models.base import PypesModel
from pypes.models.step import Step


class Pipeline(PypesModel):
    name: str
    owner: str
    resources: Dict[str, Path] = Field(default_factory=dict)
    context: Dict[str, str] = Field(default_factory=dict)
    steps: List[Step] = Field(default_factory=list)
    created: datetime = Field(default_factory=datetime.utcnow)
    known_keys: List[str] = Field(default_factory=list)

    def _check_unique_key(self, key: str):
        if key in self.known_keys:
            raise KeyAlreadyInUseException("{} is already in use!".format(key))

    def add_resources(self, new_resources: Dict[str, Path]):
        for key, path in new_resources.items():
            self._check_unique_key(key)
            self.known_keys.append(key)
            self.resources[key] = path

    def add_context(self, new_context: Dict[str, str]):
        for key, val in new_context.items():
            self._check_unique_key(key)
            self.known_keys.append(key)
            self.context[key] = val

    def get_step(self, name: str) -> Step:
        step_list = [x for x in self.steps if x.name == name]
        if not step_list:
            raise NoMatchingStepException()
        return step_list[0]


class PipelinePBS(Pipeline):
    pass
