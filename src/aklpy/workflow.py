from __future__ import annotations

import logging
from typing import Self, TypeVar
from pydantic import BaseModel, Field, PrivateAttr
from typeid import TypeID

logger = logging.getLogger(__name__)

class State(BaseModel):
    id: str = Field(default_factory=lambda: str(TypeID()), repr=False)

S = TypeVar('S', bound=State)

class Step(BaseModel):
    _stack: list[Step] = PrivateAttr(default_factory=list)

    def __or__(self, next: Step) -> Self:
        self._stack.append(next)
        return self

    async def eval(self, input: S) -> S:
        logger.info(f"Running {self.__class__.__name__} {self} with {input}")

        output = await self.work(input)
        for step in self._stack:
            logger.info(f"Running {step.__class__.__name__} {step} with {output}")
            output = await step.eval(output)

        return output

    async def work(self, input: S) -> S:
        return input
