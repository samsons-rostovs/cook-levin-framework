from tm.configuration import Configuration

class TuringMachineSimulator:

    def __init__(self):
        self.history: list[Configuration] = []

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