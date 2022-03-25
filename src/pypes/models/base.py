from pydantic import BaseModel
from typing import Literal


Outcome = Literal["error", "finished"]


class PypesModel(BaseModel):
    class Config:
        orm_mode = True
