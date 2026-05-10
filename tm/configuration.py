from dataclasses import dataclass


@dataclass
class Configuration:
    state: str
    tape: list[str]
    head_position: int
    step: int

