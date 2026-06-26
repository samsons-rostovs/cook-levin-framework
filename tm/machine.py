from dataclasses import dataclass


@dataclass
class Transition:
    next_state: str
    write_symbol: str
    move_direction: str  # "L" or "R"


class TuringMachine:
    """Single-tape, single-head Turing machine."""

    def __init__(
        self,
        states: set[str],
        input_alphabet: set[str],
        tape_alphabet: set[str],
        transitions: dict[tuple[str, str], Transition],
        start_state: str,
        accept_state: str,
        reject_state: str,
        name: str = "unnamed",
    ):
        self.states = states
        self.input_alphabet = input_alphabet
        self.tape_alphabet = tape_alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accept_state = accept_state
        self.reject_state = reject_state
        self.name = name

    def transition(self, state: str, symbol: str) -> Transition | None:
        return self.transitions.get((state, symbol))

    def describe(self) -> str:
        lines = [
            f"Turing machine: {self.name}",
            f"  States: {sorted(self.states)}",
            f"  Input alphabet: {sorted(self.input_alphabet)}",
            f"  Start: {self.start_state}, "
            f"Accept: {self.accept_state}, Reject: {self.reject_state}",
            "  Transitions:",
        ]
        for (state, symbol), move in sorted(self.transitions.items()):
            lines.append(
                f"    δ({state}, {symbol}) → "
                f"({move.next_state}, {move.write_symbol}, {move.move_direction})"
            )
        return "\n".join(lines)