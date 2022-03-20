import os
import subprocess
from datetime import datetime
from typing import Any, Dict, List, Literal, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, PrivateAttr

Status = Literal["queued", "running", "error", "finished"]


class Resource(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    path: str

    @property
    def exists(self) -> bool:
        return os.path.exists(self.path)

    @property
    def content(self) -> Union[bytes, None]:
        if self.exists:
            with open(self.path, "rb") as f:
                return f.read(1024)
        return None

    def __str__(self):
        return self.path

    def __repr__(self):
        return self.__str__()


class Step(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    status: Status = "queued"
    inputs: List[Resource] = Field(default_factory=list)
    outputs: List[Resource] = Field(default_factory=list)
    context: List[Dict[str, Any]] = Field(default_factory=list)
    command: str = ""

    _stdout: str = PrivateAttr("")
    _stderr: str = PrivateAttr("")
    _returncode: int = PrivateAttr(-1)

    def run(self) -> bool:
        self.status = "running"
        command_subbed = self.command.format(
            inputs=self.inputs, outputs=self.outputs, context=self.context
        )
        process = subprocess.Popen(
            command_subbed, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        process.wait()
        self._stdout = process.stdout.read().decode() if process.stdout else ""
        self._stderr = process.stderr.read().decode() if process.stderr else ""
        self._returncode = process.returncode
        if self._returncode > 0:
            self.status = "error"
            return False
        self.status = "finished"
        return True

    @property
    def stdout(self) -> Union[str, None]:
        if self.status in ("finished", "error"):
            return self._stdout
        return None

    @property
    def stderr(self) -> Union[str, None]:
        if self.status in ("finished", "error"):
            return self._stderr
        return None

    @property
    def returncode(self) -> Union[int, None]:
        if self.status in ("finished", "error"):
            return self._returncode
        return None


class Job(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    owner: str
    created: datetime = Field(default_factory=datetime.utcnow)
    working_dir: str
    steps: List[Step]

    @property
    def status(self):
        return all(step.status not in ("queued", "running") for step in self.steps)
