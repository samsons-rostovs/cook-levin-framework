# Changelog

## Unreleased

### Added
- Added a shared simulation-to-CNF pipeline and expanded example machine registry.
- Added CLI options for machine selection, traces, CNF summaries, DIMACS export, SAT solving, and witness control.
- Added a Streamlit web UI for tableau visualization, step tracing, SAT solving, and witness comparison.
- Added PySAT integration with a built-in DPLL fallback solver for fresh environments without optional SAT dependencies.
- Added unit tests covering simulation, tableau generation, CNF encoding, DIMACS export, and available SAT solving.

### Changed
- Reworked the Cook-Levin encoder to include structural bounded transition constraints, initial-row constraints, state-position constraints, acceptance constraints, and optional witness clauses.
- Updated tableau handling so missing cells inside the bounded rectangle are treated as blanks.
- Expanded README setup, usage, architecture, encoding overview, and roadmap documentation.

### Fixed
- Made `--no-witness --solve` meaningful by checking structural constraints instead of relying on witness-derived transition clauses.
- Ensured rejected examples can produce structural `UNSAT` results even when `python-sat` is not installed.
