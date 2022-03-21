import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Literal, Union
from uuid import uuid4

from pydantic import BaseModel, Field

from pypes.exceptions import NoMatchingStepException

Outcome = Literal["error", "finished"]


class PypesModel(BaseModel):
    class Config:
        orm_mode = True


class Step(PypesModel):
    name: str
    inputs: Dict[str, Path] = Field(default_factory=dict)
    outputs: Dict[str, Path] = Field(default_factory=dict)
    context: Dict[str, str] = Field(default_factory=dict)
    command: str = "echo {name}"


class StepRun(PypesModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    ran_at: datetime = Field(default_factory=datetime.utcnow)
    step_name: str
    outcome: Union[Outcome, None] = None
    stdout: str = ""
    stderr: str = ""
    returncode: int = -1


class Pipeline(PypesModel):
    name: str
    owner: str
    working_dir: str
    resources: Dict[str, Path] = Field(default_factory=list)
    steps: List[Step] = Field(default_factory=list)
    created: datetime = Field(default_factory=datetime.utcnow)

    def get_step(self, name: str) -> Step:
        step_list = [x for x in self.steps if x.name == name]
        if not step_list:
            raise NoMatchingStepException()
        return step_list[0]


class PipelineRun(PypesModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    ran_at: datetime = Field(default_factory=datetime.utcnow)
    pipeline_name: str
    step_runs: List[StepRun] = Field(default_factory=list)
    outcome: Union[Outcome, None] = None
