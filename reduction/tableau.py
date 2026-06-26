from tm.configuration import Configuration


def state_symbol(state: str) -> str:
    """Encode a TM state as a tableau cell symbol."""
    return f"[{state}]"


class ComputationTableau:
    """Represents the space-time diagram of a TM computation."""

    def __init__(self, configurations: list[Configuration]):
        self.configurations = configurations

    @property
    def num_steps(self) -> int:
        return max(0, len(self.configurations) - 1)

    @property
    def width(self) -> int:
        if not self.configurations:
            return 0
        return max(
            len(configuration.tape) + 1 for configuration in self.configurations
        )

    def row_at(self, step: int) -> list[str]:
        """Return tape row at a given step with the state embedded at the head."""
        configuration = self.configurations[step]
        tape = configuration.tape.copy()
        tape.insert(configuration.head_position, state_symbol(configuration.state))
        return tape

    def generate_rows(self) -> list[str]:
        return [" ".join(self.row_at(step)) for step in range(len(self.configurations))]

    def cell_symbol(self, step: int, position: int) -> str | None:
        if position >= self.width:
            return None
        row = self.row_at(step)
        if position < len(row):
            return row[position]
        return "_"
