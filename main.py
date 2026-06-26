#!/usr/bin/env python3
"""Cook–Levin framework: simulate TMs and encode computations as SAT."""

from __future__ import annotations

import argparse
import sys

from examples.machines import MACHINES
from pipeline import run_pipeline
from sat.solver import decode_tableau_from_model, solve_cnf
from visualization.tape_renderer import render_configuration


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Simulate a Turing machine and build a Cook–Levin style "
            "SAT encoding of its computation tableau."
        )
    )
    parser.add_argument("input", help="Input string for the machine")
    parser.add_argument(
        "--machine",
        "-m",
        default="ends-with-zero",
        choices=sorted(MACHINES),
        help="Which example machine to run (default: ends-with-zero)",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=100,
        help="Maximum simulation steps before halting (default: 100)",
    )
    parser.add_argument(
        "--show-tableau",
        action="store_true",
        help="Print the space-time computation tableau",
    )
    parser.add_argument(
        "--show-trace",
        action="store_true",
        help="Print step-by-step tape visualization",
    )
    parser.add_argument(
        "--show-cnf",
        action="store_true",
        help="Print CNF formula summary and sample clauses",
    )
    parser.add_argument(
        "--dimacs",
        metavar="FILE",
        help="Write the CNF formula in DIMACS format to FILE",
    )
    parser.add_argument(
        "--describe",
        action="store_true",
        help="Print the machine definition before running",
    )
    parser.add_argument(
        "--solve",
        action="store_true",
        help="Run a SAT solver on the CNF formula",
    )
    parser.add_argument(
        "--no-witness",
        action="store_true",
        help="Omit witness unit clauses from the encoding",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.describe:
        from examples.machines import get_machine

        print(get_machine(args.machine).describe())
        print()

    result = run_pipeline(
        input_word=args.input,
        machine_name=args.machine,
        max_steps=args.max_steps,
        include_witness=not args.no_witness,
    )

    show_all = not any(
        [args.show_tableau, args.show_trace, args.show_cnf, args.dimacs, args.solve]
    )

    if args.show_tableau or show_all:
        print("Computation tableau")
        print("=" * 40)
        for row in result.tableau.generate_rows():
            print(row)
        print()

    if args.show_trace or show_all:
        print("Execution trace")
        print("=" * 40)
        for configuration in result.history:
            print(render_configuration(configuration))

    if args.show_cnf or show_all:
        print("SAT encoding")
        print("=" * 40)
        print(result.formula.summary())
        witness = "yes" if not args.no_witness else "no"
        print(f"Witness clauses: {witness}")
        sample_variables = ", ".join(result.encoder.generate_variables()[:5])
        print(f"Sample variables: {sample_variables} …")
        print("Sample clauses:")
        for clause in result.formula.clauses[:5]:
            print("  (" + " ∨ ".join(clause.literals) + ")")
        if result.formula.clause_count() > 5:
            print(f"  … and {result.formula.clause_count() - 5} more clauses")
        print()

    if args.dimacs:
        with open(args.dimacs, "w", encoding="utf-8") as handle:
            handle.write(result.formula.to_dimacs())
        print(f"DIMACS formula written to {args.dimacs}")

    if args.solve or show_all:
        print("SAT solver")
        print("=" * 40)
        solve_result = solve_cnf(result.formula)
        label = (
            "SAT"
            if solve_result.satisfiable
            else "UNSAT"
            if solve_result.satisfiable is False
            else "UNKNOWN"
        )
        print(f"{solve_result.solver_name}: {label}")
        print(solve_result.message)
        if solve_result.model:
            decoded = decode_tableau_from_model(
                solve_result.model,
                num_steps=len(result.tableau.configurations),
                width=result.tableau.width,
                states=result.machine.states,
            )
            print("\nTableau from SAT model:")
            for step, row in enumerate(decoded):
                cells = [cell if cell is not None else "·" for cell in row]
                print(f"  t={step}: {' '.join(cells)}")
        print()

    print(f"Result: input {result.verdict!r} by {result.machine.name}")
    return 0 if result.verdict == "accepted" else 1


if __name__ == "__main__":
    sys.exit(main())
