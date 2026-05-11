from dataclasses import dataclass
from tm.execution_step import ExecutionStep


@dataclass
class Configuration:
    state: str
    tape: list[str]
    head_position: int
    step: int
    execution_step: ExecutionStep | None = None

