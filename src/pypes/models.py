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
        return None  # pragma: no cover

    def __str__(self):
        return self.path


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
        return None  # pragma: no cover

    @property
    def stderr(self) -> Union[str, None]:
        if self.status in ("finished", "error"):
            return self._stderr
        return None  # pragma: no cover

    @property
    def returncode(self) -> Union[int, None]:
        if self.status in ("finished", "error"):
            return self._returncode
        return None  # pragma: no cover


class Pipeline(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    owner: str
    working_dir: str
    status: Status = "queued"
    run_stderr: str = ""
    run_stdout: str = ""
    steps: List[Step] = Field()
    created: datetime = Field(default_factory=datetime.utcnow)

    def _update_run(self, step: Step):
        self.run_stdout += "\n=== {} ===\n{}".format(step.name, step.stdout)
        self.run_stderr += "\n=== {} ===\n{}".format(step.name, step.stderr)

    def run(self) -> bool:
        for step in self.steps:
            step.run()
            self._update_run(step)
            if step.returncode and step.returncode > 0:
                self.status = "error"
                return False
        self.status = "finished"
        return True
