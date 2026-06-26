from reduction.tableau import ComputationTableau, state_symbol
from sat.formula import CNFFormula
from tm.machine import Transition, TuringMachine


class TableauEncoder:
    """
    Encodes a computation tableau as a CNF formula.

    This implements a witness-based Cook–Levin style encoding: for each
    space-time cell we introduce Boolean variables C_{t}_{p}_{symbol}, then add
    structural constraints (exactly one symbol per cell, correct initial row,
    valid transitions) plus unit clauses pinning the observed computation.
    """

    def __init__(
        self,
        machine: TuringMachine,
        tableau: ComputationTableau,
        input_word: str,
    ):
        self.machine = machine
        self.tableau = tableau
        self.input_word = input_word
        self.formula = CNFFormula()
        self._symbols = self._collect_symbols()

    def _collect_symbols(self) -> list[str]:
        symbols: set[str] = set(self.machine.tape_alphabet)
        for state in self.machine.states:
            symbols.add(state_symbol(state))
        for step in range(len(self.tableau.configurations)):
            for position in range(self.tableau.width):
                symbol = self.tableau.cell_symbol(step, position)
                if symbol is not None:
                    symbols.add(symbol)
        return sorted(symbols)

    def _state_symbols(self) -> list[str]:
        return [state_symbol(state) for state in sorted(self.machine.states)]

    def _tape_symbols(self) -> list[str]:
        return sorted(self.machine.tape_alphabet)

    def cell_var(self, step: int, position: int, symbol: str) -> str:
        safe = symbol.replace("[", "").replace("]", "")
        return f"C_{step}_{position}_{safe}"

    def generate_variables(self) -> list[str]:
        variables = []
        for step in range(len(self.tableau.configurations)):
            for position in range(self.tableau.width):
                for symbol in self._symbols:
                    variables.append(self.cell_var(step, position, symbol))
        return variables

    def encode(self, include_witness: bool = True) -> CNFFormula:
        self._add_cell_uniqueness_constraints()
        self._add_state_position_constraints()
        self._add_initial_row_constraints()
        self._add_transition_constraints()
        self._add_acceptance_constraint()
        if include_witness:
            self._add_witness_clauses()
        return self.formula

    def _add_cell_uniqueness_constraints(self) -> None:
        for step in range(len(self.tableau.configurations)):
            for position in range(self.tableau.width):
                candidates = [
                    self.cell_var(step, position, symbol) for symbol in self._symbols
                ]
                self.formula.add_exactly_one(candidates)

    def _add_state_position_constraints(self) -> None:
        """Each row has exactly one state marker in a valid head position."""
        if self.tableau.width == 0:
            return

        valid_positions = range(max(0, self.tableau.width - 1))
        for step in range(len(self.tableau.configurations)):
            state_candidates = [
                self.cell_var(step, position, symbol)
                for position in valid_positions
                for symbol in self._state_symbols()
            ]
            self.formula.add_exactly_one(state_candidates)

            invalid_position = self.tableau.width - 1
            for symbol in self._state_symbols():
                self.formula.add_clause(
                    f"¬{self.cell_var(step, invalid_position, symbol)}"
                )

    def _add_initial_row_constraints(self) -> None:
        start = state_symbol(self.machine.start_state)
        self.formula.add_clause(self.cell_var(0, 0, start))

        for index, char in enumerate(self.input_word):
            self.formula.add_clause(self.cell_var(0, index + 1, char))

        for position in range(len(self.input_word) + 1, self.tableau.width):
            self.formula.add_clause(self.cell_var(0, position, "_"))

    def _add_transition_constraints(self) -> None:
        """Adjacent rows must follow one legal transition of the machine."""
        width = self.tableau.width
        if width <= 1:
            return

        tape_width = width - 1
        for step in range(len(self.tableau.configurations) - 1):
            for head in range(tape_width):
                for state in sorted(self.machine.states):
                    state_var = self.cell_var(step, head, state_symbol(state))
                    for read_symbol in self._tape_symbols():
                        read_var = self.cell_var(step, head + 1, read_symbol)
                        transition = self.machine.transition(state, read_symbol)

                        if transition is None:
                            self.formula.add_clause(f"¬{state_var}", f"¬{read_var}")
                            continue

                        next_head = self._next_head_position(
                            head, transition.move_direction
                        )
                        if next_head >= tape_width:
                            self.formula.add_clause(f"¬{state_var}", f"¬{read_var}")
                            continue

                        self._add_transition_implication(
                            step=step,
                            head=head,
                            state_var=state_var,
                            read_var=read_var,
                            transition=transition,
                            next_head=next_head,
                            tape_width=tape_width,
                        )

    @staticmethod
    def _next_head_position(head: int, direction: str) -> int:
        if direction == "R":
            return head + 1
        if direction == "L":
            return max(0, head - 1)
        return head

    @staticmethod
    def _row_position_for_tape_index(tape_index: int, head: int) -> int:
        return tape_index if tape_index < head else tape_index + 1

    def _add_transition_implication(
        self,
        step: int,
        head: int,
        state_var: str,
        read_var: str,
        transition: Transition,
        next_head: int,
        tape_width: int,
    ) -> None:
        prefix = [f"¬{state_var}", f"¬{read_var}"]
        next_state_var = self.cell_var(
            step + 1, next_head, state_symbol(transition.next_state)
        )
        self.formula.add_clause(*prefix, next_state_var)

        for tape_index in range(tape_width):
            next_position = self._row_position_for_tape_index(tape_index, next_head)
            if tape_index == head:
                self.formula.add_clause(
                    *prefix,
                    self.cell_var(step + 1, next_position, transition.write_symbol),
                )
                continue

            current_position = self._row_position_for_tape_index(tape_index, head)
            for symbol in self._tape_symbols():
                self.formula.add_clause(
                    *prefix,
                    f"¬{self.cell_var(step, current_position, symbol)}",
                    self.cell_var(step + 1, next_position, symbol),
                )

    def _add_acceptance_constraint(self) -> None:
        final_step = len(self.tableau.configurations) - 1
        accept = state_symbol(self.machine.accept_state)
        candidates = [
            self.cell_var(final_step, position, accept)
            for position in range(self.tableau.width)
        ]
        self.formula.add_clause(*candidates)

    def _add_witness_clauses(self) -> None:
        """Pin each cell to the symbol observed in the actual computation."""
        for step in range(len(self.tableau.configurations)):
            for position in range(self.tableau.width):
                symbol = self.tableau.cell_symbol(step, position)
                if symbol is not None:
                    self.formula.add_clause(
                        self.cell_var(step, position, symbol)
                    )
