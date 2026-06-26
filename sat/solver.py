"""SAT solver integration via PySAT."""

from __future__ import annotations

from dataclasses import dataclass

from sat.formula import CNFFormula

try:
    from pysat.formula import CNF
    from pysat.solvers import Glucose3

    PYSAT_AVAILABLE = True
except ImportError:
    PYSAT_AVAILABLE = False


class SearchLimitExceeded(Exception):
    """Raised when the built-in DPLL fallback reaches its search limit."""


@dataclass
class SolveResult:
    satisfiable: bool | None
    model: dict[str, bool] | None
    true_variables: list[str]
    solver_name: str
    message: str


def _formula_to_pysat(formula: CNFFormula) -> tuple[CNF, dict[int, str]]:
    if not PYSAT_AVAILABLE:
        raise ImportError(
            "python-sat is required for solving. "
            "Install with: pip install python-sat"
        )

    name_to_id = formula.dimacs_mapping()
    id_to_name = {index: name for name, index in name_to_id.items()}
    cnf = CNF()

    for clause in formula.clauses:
        dimacs_clause = []
        for literal in clause.literals:
            name = literal.lstrip("¬")
            var_id = name_to_id[name]
            if literal.startswith("¬"):
                dimacs_clause.append(-var_id)
            else:
                dimacs_clause.append(var_id)
        cnf.append(dimacs_clause)

    return cnf, id_to_name


def solve_cnf(formula: CNFFormula, solver_name: str = "glucose3") -> SolveResult:
    if not PYSAT_AVAILABLE:
        return _solve_cnf_with_dpll(formula)

    cnf, id_to_name = _formula_to_pysat(formula)
    solver = Glucose3()
    solver.append_formula(cnf)

    is_sat = solver.solve()
    if not is_sat:
        solver.delete()
        return SolveResult(
            satisfiable=False,
            model=None,
            true_variables=[],
            solver_name="Glucose3",
            message="UNSAT — no satisfying assignment exists.",
        )

    assignment = solver.get_model()
    solver.delete()

    model: dict[str, bool] = {}
    for var_id in assignment:
        name = id_to_name.get(abs(var_id))
        if name is not None:
            model[name] = var_id > 0

    true_variables = sorted(name for name, value in model.items() if value)
    return SolveResult(
        satisfiable=True,
        model=model,
        true_variables=true_variables,
        solver_name="Glucose3",
        message=f"SAT — {len(true_variables)} variables assigned true.",
    )


def _solve_cnf_with_dpll(formula: CNFFormula) -> SolveResult:
    name_to_id = formula.dimacs_mapping()
    id_to_name = {index: name for name, index in name_to_id.items()}
    clauses: list[list[int]] = []

    for clause in formula.clauses:
        dimacs_clause = []
        for literal in clause.literals:
            name = literal.lstrip("¬")
            var_id = name_to_id[name]
            dimacs_clause.append(-var_id if literal.startswith("¬") else var_id)
        clauses.append(dimacs_clause)

    try:
        assignment = _dpll(clauses, {}, max_nodes=200_000)
    except SearchLimitExceeded:
        return SolveResult(
            satisfiable=None,
            model=None,
            true_variables=[],
            solver_name="Built-in DPLL",
            message=(
                "UNKNOWN — built-in DPLL reached its search limit. "
                "Install python-sat for larger formulas."
            ),
        )

    if assignment is None:
        return SolveResult(
            satisfiable=False,
            model=None,
            true_variables=[],
            solver_name="Built-in DPLL",
            message="UNSAT — no satisfying assignment exists.",
        )

    model = {
        name: assignment.get(var_id, False)
        for var_id, name in id_to_name.items()
    }
    true_variables = sorted(name for name, value in model.items() if value)
    return SolveResult(
        satisfiable=True,
        model=model,
        true_variables=true_variables,
        solver_name="Built-in DPLL",
        message=f"SAT — {len(true_variables)} variables assigned true.",
    )


def _dpll(
    clauses: list[list[int]],
    assignment: dict[int, bool],
    max_nodes: int,
) -> dict[int, bool] | None:
    remaining_nodes = {"count": max_nodes}

    def search(current: dict[int, bool]) -> dict[int, bool] | None:
        remaining_nodes["count"] -= 1
        if remaining_nodes["count"] < 0:
            raise SearchLimitExceeded

        propagated = _propagate(clauses, current)
        if propagated is None:
            return None
        current = propagated

        if _all_clauses_satisfied(clauses, current):
            return current

        branch_var = _choose_branch_variable(clauses, current)
        if branch_var is None:
            return current

        for value in (True, False):
            branch = dict(current)
            branch[branch_var] = value
            result = search(branch)
            if result is not None:
                return result
        return None

    return search(dict(assignment))


def _propagate(
    clauses: list[list[int]],
    assignment: dict[int, bool],
) -> dict[int, bool] | None:
    current = dict(assignment)

    while True:
        changed = False
        unit_literals = _find_unit_literals(clauses, current)
        if not unit_literals:
            if _has_empty_clause(clauses, current):
                return None
        else:
            for literal in unit_literals:
                if not _assign_literal(current, literal):
                    return None
                changed = True

        pure_literals = _find_pure_literals(clauses, current)
        for literal in pure_literals:
            if not _assign_literal(current, literal):
                return None
            changed = True

        if not changed:
            return current


def _assign_literal(assignment: dict[int, bool], literal: int) -> bool:
    variable = abs(literal)
    value = literal > 0
    previous = assignment.get(variable)
    if previous is not None:
        return previous == value
    assignment[variable] = value
    return True


def _find_unit_literals(
    clauses: list[list[int]],
    assignment: dict[int, bool],
) -> list[int]:
    units = []
    for clause in clauses:
        if _clause_satisfied(clause, assignment):
            continue
        unassigned = [
            literal for literal in clause if abs(literal) not in assignment
        ]
        if len(unassigned) == 1:
            units.append(unassigned[0])
    return units


def _has_empty_clause(
    clauses: list[list[int]],
    assignment: dict[int, bool],
) -> bool:
    for clause in clauses:
        if _clause_satisfied(clause, assignment):
            continue
        if all(abs(literal) in assignment for literal in clause):
            return True
    return False


def _find_pure_literals(
    clauses: list[list[int]],
    assignment: dict[int, bool],
) -> list[int]:
    polarities: dict[int, set[bool]] = {}
    for clause in clauses:
        if _clause_satisfied(clause, assignment):
            continue
        for literal in clause:
            variable = abs(literal)
            if variable in assignment:
                continue
            polarities.setdefault(variable, set()).add(literal > 0)

    return [
        variable if next(iter(values)) else -variable
        for variable, values in polarities.items()
        if len(values) == 1
    ]


def _choose_branch_variable(
    clauses: list[list[int]],
    assignment: dict[int, bool],
) -> int | None:
    scores: dict[int, int] = {}
    for clause in clauses:
        if _clause_satisfied(clause, assignment):
            continue
        for literal in clause:
            variable = abs(literal)
            if variable not in assignment:
                scores[variable] = scores.get(variable, 0) + 1
    if not scores:
        return None
    return max(scores, key=scores.get)


def _all_clauses_satisfied(
    clauses: list[list[int]],
    assignment: dict[int, bool],
) -> bool:
    return all(_clause_satisfied(clause, assignment) for clause in clauses)


def _clause_satisfied(clause: list[int], assignment: dict[int, bool]) -> bool:
    for literal in clause:
        value = assignment.get(abs(literal))
        if value is not None and value == (literal > 0):
            return True
    return False


def decode_tableau_from_model(
    model: dict[str, bool],
    num_steps: int,
    width: int,
    states: set[str] | None = None,
) -> list[list[str | None]]:
    """Reconstruct tableau cell symbols from C_* variable assignments."""
    grid: list[list[str | None]] = [
        [None for _ in range(width)] for _ in range(num_steps)
    ]
    state_names = states or set()

    for name, value in model.items():
        if not value or not name.startswith("C_"):
            continue
        parts = name.split("_", 3)
        if len(parts) != 4:
            continue
        _, step_text, position_text, symbol = parts
        try:
            step = int(step_text)
            position = int(position_text)
        except ValueError:
            continue
        if step >= num_steps or position >= width:
            continue
        display = f"[{symbol}]" if symbol in state_names else symbol
        grid[step][position] = display

    return grid
