from typing import TypeGuard, Union

from pypes.models.step import Step, StepPBS


def is_step(obj: Union[Step, StepPBS]) -> TypeGuard[Step]:
    if type(obj) == Step:
        return True
    return False


def is_pbs_step(obj: Union[Step, StepPBS]) -> TypeGuard[StepPBS]:
    if type(obj) == StepPBS:
        return True
    return False
