"""Shared simulation + encoding pipeline."""

from __future__ import annotations

from dataclasses import dataclass

from examples.machines import get_machine
from reduction.encoding import TableauEncoder
from reduction.tableau import ComputationTableau
from sat.formula import CNFFormula
from tm.configuration import Configuration
from tm.machine import TuringMachine
from tm.simulator import TuringMachineSimulator


@dataclass
class RunResult:
    machine: TuringMachine
    input_word: str
    final_state: str
    verdict: str
    history: list[Configuration]
    tableau: ComputationTableau
    encoder: TableauEncoder
    formula: CNFFormula


def verdict(final_state: str, machine: TuringMachine) -> str:
    if final_state == machine.accept_state:
        return "accepted"
    if final_state == machine.reject_state:
        return "rejected"
    return "halted (no accept/reject)"


def run_pipeline(
    input_word: str,
    machine_name: str = "ends-with-zero",
    max_steps: int = 100,
    include_witness: bool = True,
) -> RunResult:
    machine = get_machine(machine_name)
    simulator = TuringMachineSimulator(machine)
    final_state = simulator.simulate(input_word, max_steps=max_steps)
    history = simulator.get_history()
    tableau = ComputationTableau(history)
    encoder = TableauEncoder(machine, tableau, input_word)
    formula = encoder.encode(include_witness=include_witness)
    return RunResult(
        machine=machine,
        input_word=input_word,
        final_state=final_state,
        verdict=verdict(final_state, machine),
        history=history,
        tableau=tableau,
        encoder=encoder,
        formula=formula,
    )
