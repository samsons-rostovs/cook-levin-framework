"""HTML rendering for computation tableaux."""

from __future__ import annotations

from reduction.tableau import ComputationTableau

_TABLEAU_STYLES = """
<style>
.tableau-wrap {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  overflow-x: auto;
}
.tableau-wrap h3 {
  margin: 0 0 0.75rem 0;
  font-family: system-ui, sans-serif;
}
.tableau {
  border-collapse: collapse;
  width: 100%;
}
.tableau th, .tableau td {
  border: 1px solid #334155;
  padding: 0.35rem 0.55rem;
  text-align: center;
  min-width: 2rem;
}
.tableau th {
  background: #1e293b;
  color: #e2e8f0;
  font-weight: 600;
}
.tableau td.cell {
  background: #0f172a;
  color: #f8fafc;
}
.tableau td.state {
  background: #1d4ed8;
  color: #eff6ff;
  font-weight: 700;
}
.tableau td.blank {
  background: #111827;
  color: #64748b;
}
.tableau td.marked {
  background: #7c3aed;
  color: #f5f3ff;
}
.tableau td.symbol {
  background: #0f172a;
  color: #f8fafc;
}
.legend {
  display: flex;
  gap: 1rem;
  margin-top: 0.75rem;
  font-size: 0.85rem;
  color: #cbd5e1;
  font-family: system-ui, sans-serif;
}
.legend span {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}
.swatch {
  width: 0.85rem;
  height: 0.85rem;
  border-radius: 2px;
  display: inline-block;
}
</style>
"""


def _cell_class(symbol: str) -> str:
    if symbol.startswith("[") and symbol.endswith("]"):
        return "state"
    if symbol == "_":
        return "blank"
    if symbol == "X":
        return "marked"
    return "symbol"


def _format_symbol(symbol: str) -> str:
    return symbol.replace("[", "").replace("]", "")


def render_tableau_html(tableau: ComputationTableau, title: str = "Computation Tableau") -> str:
    rows = [tableau.row_at(step) for step in range(len(tableau.configurations))]
    if not rows:
        return "<p>No computation to display.</p>"

    width = max(len(row) for row in rows)
    header = "".join(f"<th>#{index}</th>" for index in range(width))
    body_rows = []

    for step, row in enumerate(rows):
        cells = []
        for index in range(width):
            symbol = row[index] if index < len(row) else "_"
            css_class = _cell_class(symbol)
            cells.append(
                f'<td class="cell {css_class}">{_format_symbol(symbol)}</td>'
            )
        body_rows.append(f"<tr><th>t={step}</th>{''.join(cells)}</tr>")

    return f"""
{_TABLEAU_STYLES}
<div class="tableau-wrap">
  <h3>{title}</h3>
  <table class="tableau">
    <thead><tr><th>time</th>{header}</tr></thead>
    <tbody>{''.join(body_rows)}</tbody>
  </table>
  <div class="legend">
    <span><i class="swatch" style="background:#1d4ed8"></i> state</span>
    <span><i class="swatch" style="background:#0f172a;border:1px solid #334155"></i> tape symbol</span>
    <span><i class="swatch" style="background:#7c3aed"></i> marked</span>
    <span><i class="swatch" style="background:#111827;border:1px solid #334155"></i> blank</span>
  </div>
</div>
"""


def render_step_trace_html(
    tableau: ComputationTableau,
    step: int,
    machine_states: set[str] | None = None,
) -> str:
    row = tableau.row_at(step)
    cells = []
    for symbol in row:
        css_class = _cell_class(symbol)
        cells.append(f'<td class="cell {css_class}">{_format_symbol(symbol)}</td>')

    configuration = tableau.configurations[step]
    transition = ""
    if configuration.execution_step is not None:
        move = configuration.execution_step
        transition = (
            f"δ({configuration.state}, {move.read_symbol}) → "
            f"({move.next_state}, {move.write_symbol}, {move.move_direction})"
        )

    return f"""
{_TABLEAU_STYLES}
<div class="tableau-wrap">
  <h3>Step {step} — state {configuration.state}</h3>
  <table class="tableau"><tr>{''.join(cells)}</tr></table>
  <p style="color:#cbd5e1;font-family:system-ui,sans-serif;margin-top:0.75rem;">
    Head column (with state embedded): position {configuration.head_position}
    {f" · {transition}" if transition else ""}
  </p>
</div>
"""


def render_model_tableau_html(
    grid: list[list[str | None]],
    title: str = "Tableau decoded from SAT model",
) -> str:
    if not grid:
        return "<p>No model tableau to display.</p>"

    width = max(len(row) for row in grid)
    header = "".join(f"<th>#{index}</th>" for index in range(width))
    body_rows = []

    for step, row in enumerate(grid):
        cells = []
        for index in range(width):
            symbol = row[index] if index < len(row) and row[index] is not None else "·"
            css_class = _cell_class(symbol) if symbol != "·" else "blank"
            display = _format_symbol(symbol) if symbol != "·" else "·"
            cells.append(f'<td class="cell {css_class}">{display}</td>')
        body_rows.append(f"<tr><th>t={step}</th>{''.join(cells)}</tr>")

    return f"""
{_TABLEAU_STYLES}
<div class="tableau-wrap">
  <h3>{title}</h3>
  <table class="tableau">
    <thead><tr><th>time</th>{header}</tr></thead>
    <tbody>{''.join(body_rows)}</tbody>
  </table>
</div>
"""
