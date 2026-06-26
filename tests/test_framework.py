import unittest

from examples.machines import ends_with_zero, get_machine, palindrome
from pipeline import run_pipeline
from reduction.encoding import TableauEncoder
from reduction.tableau import ComputationTableau, state_symbol
from sat.formula import CNFFormula
from sat.solver import PYSAT_AVAILABLE, decode_tableau_from_model, solve_cnf
from tm.simulator import TuringMachineSimulator


class TestSimulator(unittest.TestCase):
    def test_ends_with_zero_accepts(self) -> None:
        machine = ends_with_zero()
        simulator = TuringMachineSimulator(machine)
        self.assertEqual(simulator.simulate("1010"), machine.accept_state)

    def test_ends_with_zero_rejects_all_ones(self) -> None:
        machine = ends_with_zero()
        simulator = TuringMachineSimulator(machine)
        self.assertNotEqual(simulator.simulate("111"), machine.accept_state)

    def test_palindrome_accepts(self) -> None:
        machine = palindrome()
        simulator = TuringMachineSimulator(machine)
        self.assertEqual(simulator.simulate("0110"), machine.accept_state)

    def test_palindrome_rejects(self) -> None:
        machine = palindrome()
        simulator = TuringMachineSimulator(machine)
        self.assertNotEqual(simulator.simulate("011"), machine.accept_state)

    def test_history_records_steps(self) -> None:
        machine = ends_with_zero()
        simulator = TuringMachineSimulator(machine)
        simulator.simulate("10")
        self.assertEqual(len(simulator.get_history()), 3)


class TestTableau(unittest.TestCase):
    def test_state_symbol_embedded_at_head(self) -> None:
        machine = ends_with_zero()
        simulator = TuringMachineSimulator(machine)
        simulator.simulate("10")
        tableau = ComputationTableau(simulator.get_history())
        self.assertIn(state_symbol("q0"), tableau.row_at(0))


class TestEncoding(unittest.TestCase):
    def test_cnf_formula_has_clauses(self) -> None:
        machine = ends_with_zero()
        simulator = TuringMachineSimulator(machine)
        simulator.simulate("10")
        tableau = ComputationTableau(simulator.get_history())
        encoder = TableauEncoder(machine, tableau, "10")
        formula = encoder.encode()
        self.assertGreater(formula.clause_count(), 0)
        self.assertGreater(formula.variable_count(), 0)

    def test_dimacs_export(self) -> None:
        formula = CNFFormula()
        formula.add_clause("x", "y")
        formula.add_clause("¬x", "z")
        dimacs = formula.to_dimacs()
        self.assertTrue(dimacs.startswith("p cnf"))
        self.assertIn(" 0", dimacs)

    def test_exactly_one_encoding(self) -> None:
        formula = CNFFormula()
        formula.add_exactly_one(["a", "b", "c"])
        self.assertEqual(formula.clause_count(), 4)

    def test_unknown_machine_raises(self) -> None:
        with self.assertRaises(KeyError):
            get_machine("does-not-exist")

    def test_encode_without_witness(self) -> None:
        result = run_pipeline("10", include_witness=False)
        witness_vars = [
            clause.literals[0]
            for clause in result.formula.clauses
            if len(clause.literals) == 1 and not clause.literals[0].startswith("¬")
        ]
        with_witness = run_pipeline("10", include_witness=True)
        witness_with = [
            clause.literals[0]
            for clause in with_witness.formula.clauses
            if len(clause.literals) == 1 and not clause.literals[0].startswith("¬")
        ]
        self.assertLess(len(witness_vars), len(witness_with))


class TestAvailableSolver(unittest.TestCase):
    def test_accepting_input_is_sat_with_available_solver(self) -> None:
        result = run_pipeline("10")
        solve_result = solve_cnf(result.formula)
        self.assertTrue(solve_result.satisfiable)
        self.assertIsNotNone(solve_result.model)

    def test_rejected_input_unsat_without_witness_with_available_solver(self) -> None:
        result = run_pipeline("111", include_witness=False)
        solve_result = solve_cnf(result.formula)
        self.assertFalse(solve_result.satisfiable)


@unittest.skipUnless(PYSAT_AVAILABLE, "python-sat not installed")
class TestSolver(unittest.TestCase):
    def test_accepting_input_is_sat(self) -> None:
        result = run_pipeline("10")
        solve_result = solve_cnf(result.formula)
        self.assertTrue(solve_result.satisfiable)
        self.assertIsNotNone(solve_result.model)

    def test_rejected_input_unsat_without_witness(self) -> None:
        result = run_pipeline("111", include_witness=False)
        solve_result = solve_cnf(result.formula)
        self.assertFalse(solve_result.satisfiable)

    def test_decode_tableau_from_model(self) -> None:
        result = run_pipeline("10")
        solve_result = solve_cnf(result.formula)
        assert solve_result.model is not None
        grid = decode_tableau_from_model(
            solve_result.model,
            num_steps=len(result.tableau.configurations),
            width=result.tableau.width,
            states=result.machine.states,
        )
        self.assertEqual(grid[0][0], state_symbol("q0"))


if __name__ == "__main__":
    unittest.main()
