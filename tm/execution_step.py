from dataclasses import dataclass


@dataclass
class ExecutionStep:
    read_symbol: str
    write_symbol: str
    move_direction: str
    next_state: str