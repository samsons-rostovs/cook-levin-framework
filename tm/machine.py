from dataclasses import dataclass


@dataclass
class Transition:
    next_state: str
    write_symbol: str
    move_direction: str


class TuringMachine:

    def __init__(
        self,
        states: set[str],
        input_alphabet: set[str],
        tape_alphabet: set[str],
        transitions: dict[tuple[str, str], Transition],
        start_state: str,
        accept_state: str,
        reject_state: str
    ):
        
        self.states = states
        self.input_alphabet = input_alphabet
        self.tape_alphabet = tape_alphabet
        self.transitions = transitions
        
        self.start_state = start_state
        self.accept_state = accept_state
        self.reject_state = reject_state