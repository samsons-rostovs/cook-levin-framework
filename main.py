from tm.simulator import TuringMachineSimulator
from visualization.tape_renderer import render_configuration


simulator = TuringMachineSimulator()

simulator.add_configuration(
    state="q0",
    tape=["1", "0", "1", "_"],
    head_position=0,
    step=0
)

simulator.add_configuration(
    state="q1",
    tape=["1", "0", "1", "_"],
    head_position=1,
    step=1
)

for configuration in simulator.get_history():
    print(render_configuration(configuration))