from typing import Any, Callable, Awaitable

# A step is an async function: dict -> dict
StepFn = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]


class Pipeline:
    """A simple sequential async pipeline that passes data through steps."""

    def __init__(self) -> None:
        self._steps: list[StepFn] = []

    def add_step(self, step: StepFn) -> "Pipeline":
        self._steps.append(step)
        return self

    async def run(self, initial_data: dict[str, Any]) -> dict[str, Any]:
        data = initial_data
        for step in self._steps:
            data = await step(data)
        return data
