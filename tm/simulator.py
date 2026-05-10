from tm.configuration import Configuration
from tm.machine import TuringMachine


class TuringMachineSimulator:

    def __init__(self, machine: TuringMachine):

        self.machine = machine
        self.history: list[Configuration] = []

    def simulate(self, input_word: str, max_steps: int = 100):

        tape = list(input_word) + ["_"]
        current_state = self.machine.start_state
        head_position = 0
        step = 0

        self.add_configuration(
            current_state,
            tape,
            head_position,
            step
        )

        while (
            current_state != self.machine.accept_state
            and current_state != self.machine.reject_state
            and step < max_steps
        ):
            current_symbol = tape[head_position]
            transition_key = (current_state, current_symbol)

            if transition_key not in self.machine.transitions:
                break

            transition = self.machine.transitions[transition_key]
            tape[head_position] = transition.write_symbol
            current_state = transition.next_state

            if transition.move_direction == "R":
                head_position += 1
                if head_position >= len(tape):
                    tape.append("_")
            elif transition.move_direction == "L":
                head_position = max(0, head_position - 1)
            
            step += 1
            self.add_configuration(
                current_state,
                tape,
                head_position,
                step
            )

    def add_configuration(
            self,
            state: str,
            tape: list[str],
            head_position: int,
            step: int
    ) -> None:
        
        configuration = Configuration(
            state=state,
            tape=tape.copy(),
            head_position=head_position,
            step=step
        )

        self.history.append(configuration)

    def get_history(self) -> list[Configuration]:
        return self.history