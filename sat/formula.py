from dataclasses import dataclass, field


@dataclass
class Variable:
    name: str


@dataclass
class Clause:
    literals: list[str] = field(default_factory=list)


class CNFFormula:
    """Conjunctive normal form (CNF) Boolean formula."""

    def __init__(self) -> None:
        self.clauses: list[Clause] = []

    def add_clause(self, *literals: str) -> None:
        if literals:
            self.clauses.append(Clause(list(literals)))

    def add_exactly_one(self, variables: list[str]) -> None:
        """At least one and at most one of the variables may be true."""
        if not variables:
            return
        self.add_clause(*variables)
        for i, left in enumerate(variables):
            for right in variables[i + 1 :]:
                self.add_clause(f"¬{left}", f"¬{right}")

    def clause_count(self) -> int:
        return len(self.clauses)

    def variable_count(self) -> int:
        variables: set[str] = set()
        for clause in self.clauses:
            for literal in clause.literals:
                variables.add(literal.lstrip("¬"))
        return len(variables)

    def to_dimacs(self) -> str:
        """Export the formula in DIMACS CNF format."""
        lines = [
            f"p cnf {self.variable_count()} {self.clause_count()}",
        ]
        for clause in self.clauses:
            parts = []
            for literal in clause.literals:
                name = literal.lstrip("¬")
                sign = "-" if literal.startswith("¬") else ""
                parts.append(f"{sign}{self._dimacs_id(name)}")
            lines.append(" ".join(parts) + " 0")
        return "\n".join(lines)

    def dimacs_mapping(self) -> dict[str, int]:
        """Map variable names to positive DIMACS integer ids."""
        if not hasattr(self, "_dimacs_map"):
            names = sorted(
                {
                    literal.lstrip("¬")
                    for clause in self.clauses
                    for literal in clause.literals
                }
            )
            self._dimacs_map = {name: index + 1 for index, name in enumerate(names)}
        return dict(self._dimacs_map)

    def _dimacs_id(self, name: str) -> int:
        return self.dimacs_mapping()[name]

    def summary(self) -> str:
        return (
            f"CNF formula: {self.variable_count()} variables, "
            f"{self.clause_count()} clauses"
        )
