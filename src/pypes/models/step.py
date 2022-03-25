from pathlib import Path
from typing import Dict, List

from pydantic import Field
from pypes.models.base import PypesModel


class Step(PypesModel):
    name: str
    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    command: str = "echo {name}"


class StepPBS(Step):
    pass
