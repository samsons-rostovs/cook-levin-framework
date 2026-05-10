from tm.machine import TuringMachine, Transition
from tm.simulator import TuringMachineSimulator
from visualization.tape_renderer import render_configuration


transitions = {
    ("q0", "1"): Transition(
        next_state="q1",
        write_symbol="1",
        move_direction="R"
    ),

    ("q1", "0"): Transition(
        next_state="q_accept",
        write_symbol="0",
        move_direction="R"
    )
}


machine = TuringMachine(
    states={"q0", "q1", "q_accept", "q_reject"},

    input_alphabet={"0", "1"},

    tape_alphabet={"0", "1", "_"},

    transitions=transitions,

    start_state="q0",

    accept_state="q_accept",

    reject_state="q_reject"
)


simulator = TuringMachineSimulator(machine)

simulator.simulate("10")


for configuration in simulator.get_history():
    print(render_configuration(configuration))