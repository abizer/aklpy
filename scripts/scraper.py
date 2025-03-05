from __future__ import annotations

import asyncio
import logging

import httpx
import llm
from pydantic import Field, HttpUrl
from rich.logging import RichHandler

from akl.workflow import State, Step

logger = logging.getLogger(__name__)


def httpx_client(api_key: str | None = None):
    return httpx.AsyncClient(
        follow_redirects=True,
        timeout=httpx.Timeout(10.0, read=None, connect=None),
    )


class Target(State):
    url: HttpUrl


class Fetched(Target):
    result: str


class Fetch(Step, arbitrary_types_allowed=True):
    client: httpx.AsyncClient = Field(
        default_factory=httpx_client, repr=False, exclude=True
    )

    async def work(self, input: Target) -> Fetched:
        response = await self.client.get(str(input.url))
        response.raise_for_status()
        return Fetched(result=response.text, **input.model_dump())


class Processed(Fetched):
    summary: str


class Process(Step, arbitrary_types_allowed=True):
    model: llm.AsyncModel = Field(default=llm.get_async_model("gpt-4o-mini"))
    prompt: str = "Summarize the following text: {result}"

    async def work(self, input: Fetched) -> Processed:
        response = await self.model.prompt(self.prompt.format(**input.model_dump()))
        return Processed(summary=await response.text(), **input.model_dump())


async def main() -> None:
    target = Target(url="https://abizer.me")
    p = Fetch() | Process()
    logger.info(await p.eval(target))


if __name__ == "__main__":
    logging.basicConfig(
        level="INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)],
    )
    asyncio.run(main())
