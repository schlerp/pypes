from typing import Union, List
from pydantic import Field
from datetime import datetime
from uuid import uuid4
from pypes.models.base import PypesModel, Outcome
from pypes.models.pipeline import Pipeline


class StepRun(PypesModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    ran_at: datetime = Field(default_factory=datetime.utcnow)
    step_name: str
    outcome: Union[Outcome, None] = None
    stdout: str = ""
    stderr: str = ""
    returncode: int = -1


class PipelineRun(PypesModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    ran_at: datetime = Field(default_factory=datetime.utcnow)
    pipeline: Pipeline
    step_runs: List[StepRun] = Field(default_factory=list)
    outcome: Union[Outcome, None] = None
