"""Streamlit web UI for the Cook–Levin framework."""

from __future__ import annotations

import streamlit as st

from examples.machines import MACHINES
from pipeline import run_pipeline
from sat.solver import PYSAT_AVAILABLE, decode_tableau_from_model, solve_cnf
from visualization.tableau_html import (
    render_model_tableau_html,
    render_step_trace_html,
    render_tableau_html,
)
from visualization.tape_renderer import render_configuration


def solver_label(satisfiable: bool | None) -> str:
    if satisfiable is True:
        return "SAT"
    if satisfiable is False:
        return "UNSAT"
    return "UNKNOWN"


st.set_page_config(
    page_title="Cook–Levin Framework",
    page_icon="🧮",
    layout="wide",
)

st.title("Cook–Levin Framework")
st.caption(
    "Simulate Turing machines, visualize computation tableaux, "
    "and solve Cook–Levin SAT encodings."
)

with st.sidebar:
    st.header("Configuration")
    machine_name = st.selectbox(
        "Machine",
        options=sorted(MACHINES),
        format_func=lambda key: f"{key} — {MACHINES[key].name}",
    )
    input_word = st.text_input("Input string", value="1010")
    max_steps = st.slider("Max steps", min_value=10, max_value=500, value=100)
    include_witness = st.checkbox(
        "Include witness clauses",
        value=True,
        help="Pin the observed computation as unit clauses in the CNF formula.",
    )
    run_clicked = st.button("Run simulation", type="primary", use_container_width=True)

    with st.expander("Machine definition"):
        st.code(MACHINES[machine_name].describe(), language=None)

if run_clicked:
    if not input_word:
        st.error("Please enter an input string.")
    else:
        with st.spinner("Simulating and encoding…"):
            result = run_pipeline(
                input_word=input_word,
                machine_name=machine_name,
                max_steps=max_steps,
                include_witness=include_witness,
            )
        st.session_state["result"] = result
        st.session_state["include_witness"] = include_witness

if "result" not in st.session_state:
    st.info("Choose a machine and input, then click **Run simulation**.")
    st.stop()

result = st.session_state["result"]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Machine", result.machine.name)
col2.metric("Input", result.input_word)
col3.metric("Verdict", result.verdict)
col4.metric("Steps", len(result.history) - 1)

tab_tableau, tab_trace, tab_sat, tab_compare = st.tabs(
    ["Tableau", "Step trace", "SAT solver", "Compare"]
)

with tab_tableau:
    st.markdown(
        render_tableau_html(result.tableau, "Space–time computation tableau"),
        unsafe_allow_html=True,
    )

with tab_trace:
    step = st.slider(
        "Step",
        min_value=0,
        max_value=max(0, len(result.history) - 1),
        value=0,
    )
    st.markdown(
        render_step_trace_html(result.tableau, step, result.machine.states),
        unsafe_allow_html=True,
    )
    with st.expander("ASCII trace detail"):
        st.text(render_configuration(result.history[step]))

with tab_sat:
    st.subheader("CNF encoding")
    st.write(result.formula.summary())
    st.write(
        f"Witness clauses: **{'enabled' if st.session_state.get('include_witness', True) else 'disabled'}**"
    )

    sample_clauses = result.formula.clauses[:8]
    st.code(
        "\n".join(
            "(" + " ∨ ".join(clause.literals) + ")"
            for clause in sample_clauses
        )
        + (
            f"\n… and {result.formula.clause_count() - 8} more"
            if result.formula.clause_count() > 8
            else ""
        ),
        language=None,
    )

    st.subheader("SAT solver")
    if not PYSAT_AVAILABLE:
        st.info(
            "Using the built-in DPLL solver. Install `python-sat` for faster "
            "solving on larger formulas."
        )

    if st.button("Solve CNF", type="primary"):
        spinner_text = "Running Glucose3…" if PYSAT_AVAILABLE else "Running DPLL…"
        with st.spinner(spinner_text):
            solve_result = solve_cnf(result.formula)
        st.session_state["solve_result"] = solve_result

    if "solve_result" in st.session_state:
        solve_result = st.session_state["solve_result"]
        if solve_result.satisfiable:
            st.success(f"{solve_result.solver_name}: SAT")
        elif solve_result.satisfiable is False:
            st.error(f"{solve_result.solver_name}: UNSAT")
        else:
            st.warning(solve_result.message)

        st.write(solve_result.message)

        if solve_result.model:
            decoded = decode_tableau_from_model(
                solve_result.model,
                num_steps=len(result.tableau.configurations),
                width=result.tableau.width,
                states=result.machine.states,
            )
            st.markdown(
                render_model_tableau_html(
                    decoded, "Tableau reconstructed from SAT model"
                ),
                unsafe_allow_html=True,
            )
            with st.expander(
                f"True variables ({len(solve_result.true_variables)})"
            ):
                st.code("\n".join(solve_result.true_variables[:100]), language=None)
                if len(solve_result.true_variables) > 100:
                    st.caption(
                        f"… and {len(solve_result.true_variables) - 100} more"
                    )

with tab_compare:
    st.write(
        "Compare structural-only vs witness-augmented encodings. "
        "With witness clauses disabled, rejected inputs often become UNSAT "
        "because the acceptance constraint cannot be met."
    )
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**With witness (current run)**")
        sr = solve_cnf(result.formula)
        st.write(solver_label(sr.satisfiable))

    with c2:
        st.markdown("**Structural only (no witness)**")
        structural = run_pipeline(
            input_word=result.input_word,
            machine_name=machine_name,
            max_steps=max_steps,
            include_witness=False,
        )
        sr = solve_cnf(structural.formula)
        st.write(solver_label(sr.satisfiable))
        st.caption(structural.formula.summary())
