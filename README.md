# Cook-Levin Framework

Interactive framework for simulating Turing machines and visualizing the [Cook–Levin reduction](https://en.wikipedia.org/wiki/Cook%E2%80%93Levin_theorem) to SAT.

This project was inspired by a university seminar on computability and complexity theory at ETH Zürich. It is being developed as an educational tool for exploring how nondeterministic polynomial-time computations can be encoded as Boolean satisfiability problems.

## What it does

1. **Simulate** a single-tape Turing machine step by step
2. **Record** a space–time *computation tableau* (configuration history)
3. **Encode** the tableau as a CNF Boolean formula in Cook–Levin style
4. **Solve** the formula with [PySAT](https://pysathq.github.io/) (Glucose3) or the built-in DPLL fallback
5. **Visualize** interactively in a Streamlit web UI

## Quick start

```bash
# Install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# CLI
python3 main.py 1010
python3 main.py 0110 --machine palindrome --solve
python3 main.py 111 --no-witness --solve          # UNSAT (no accepting tableau)

# Web UI
streamlit run web/app.py

# Tests
python3 -m unittest discover -s tests -v
```

## Example output

```
SAT solver
========================================
Built-in DPLL: SAT
SAT — 12 variables assigned true.

Tableau from SAT model:
  t=0: [q0] 1 0 _
  t=1: 1 [q1] 0 _
  t=2: 1 0 [q_accept] _

Result: input 'accepted' by ends-with-zero
```

## Architecture

```
main.py                  CLI entry point
web/app.py               Streamlit web UI
pipeline.py              Shared simulate → encode pipeline
tm/
  machine.py             Turing machine model (states, transitions)
  simulator.py           Step-by-step execution with history
  configuration.py       Snapshot of tape + head + state
reduction/
  tableau.py             Space–time diagram from configuration history
  encoding.py            Cook–Levin style CNF construction
sat/
  formula.py             CNF data structure + DIMACS export
  solver.py              PySAT/DPLL solving + model decoding
examples/
  machines.py            Example machines (ends-with-zero, palindrome)
visualization/
  tape_renderer.py       ASCII tape / head display
  tableau_html.py        Colored HTML tableau for the web UI
```

## Cook–Levin encoding (overview)

Given a machine `M` and input `x`, the encoder builds a CNF formula `φ` that is satisfiable when the recorded tableau is a valid accepting computation.

| Constraint | Meaning |
|---|---|
| **Cell uniqueness** | Each space–time cell holds exactly one symbol |
| **Initial row** | Row 0 matches the input and start state |
| **Transition** | Each row follows from the previous via a valid bounded TM transition |
| **Acceptance** | Some cell in the final row contains the accept state |
| **Witness** (optional) | Unit clauses pinning the observed computation |

Variables are named `C_{time}_{position}_{symbol}` (e.g. `C_0_0_q0`).

Use `--no-witness` to drop witness clauses and test whether the structural constraints alone admit a satisfying assignment.

## Example machines

| Name | Language |
|---|---|
| `ends-with-zero` | Binary strings with a `1` followed by a `0` |
| `palindrome` | Binary palindromes over `{0, 1}` |

Add new machines in `examples/machines.py` and register them in the `MACHINES` dict.

## CLI options

```
usage: main.py [-h] [--machine {ends-with-zero,palindrome}] [--max-steps MAX_STEPS]
               [--show-tableau] [--show-trace] [--show-cnf] [--dimacs FILE]
               [--describe] [--solve] [--no-witness]
               input
```

## Web UI

The Streamlit app provides:

- **Tableau** — colored space–time grid (states highlighted in blue)
- **Step trace** — slider through individual configurations
- **SAT solver** — run Glucose3 or the built-in DPLL fallback and decode the satisfying assignment back into a tableau
- **Compare** — structural-only vs witness-augmented satisfiability

## Roadmap

- [x] Structural transition constraints (without witness clauses)
- [ ] NP-completeness pipeline: reduce 3-SAT → TM → CNF
- [x] Interactive web visualization
- [x] Integration with SAT solving (`python-sat` when installed, built-in DPLL otherwise)

## Background reading

- M. Sipser, *Introduction to the Theory of Computation* — Cook–Levin theorem
- S. Arora & B. Barak, *Computational Complexity* — NP-completeness and reductions

## License

See [LICENSE](LICENSE).
