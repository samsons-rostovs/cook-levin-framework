from examples.simple_machine import simple_machine
from tm.simulator import TuringMachineSimulator
from visualization.tape_renderer import render_configuration


simulator = TuringMachineSimulator(simple_machine)
simulator.simulate("10")

for configuration in simulator.get_history():
    print(render_configuration(configuration))