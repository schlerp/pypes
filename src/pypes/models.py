import os
from datetime import datetime
from typing import Any, Dict, List, Literal, Union
from uuid import uuid4

from pydantic import BaseModel, Field

from pypes.exceptions import NoMatchingStepException

Outcome = Literal["error", "finished"]


class Resource(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    path: str

    @property
    def exists(self) -> bool:
        return os.path.exists(self.path)

    def read(self, block_size: int = 1024) -> bytes:
        if self.exists:
            with open(self.path, "rb") as f:
                return f.read(block_size)
        return b""  # pragma: no cover

    def __str__(self):
        return self.path


class Step(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    name: str
    inputs: List[Resource] = Field(default_factory=list)
    outputs: List[Resource] = Field(default_factory=list)
    context: List[Dict[str, Any]] = Field(default_factory=list)
    command: str = ""


class StepRun(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    ran_at: datetime = Field(default_factory=datetime.utcnow)
    step_id: str
    outcome: Union[Outcome, None] = None
    stdout: str = ""
    stderr: str = ""
    returncode: int = -1


class Pipeline(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    name: str
    owner: str
    working_dir: str
    steps: List[Step] = Field()
    created: datetime = Field(default_factory=datetime.utcnow)

    def get_step(self, id: str) -> Step:
        step_list = [x for x in self.steps if x.id == id]
        if not step_list:
            raise NoMatchingStepException()
        return step_list[0]


class PipelineRun(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    ran_at: datetime = Field(default_factory=datetime.utcnow)
    pipeline_id: str
    step_runs: List[StepRun] = Field(default_factory=list)
    outcome: Union[Outcome, None] = None
