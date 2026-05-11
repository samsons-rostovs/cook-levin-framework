import sys
from examples.simple_machine import simple_machine
from tm.simulator import TuringMachineSimulator
from visualization.tape_renderer import render_configuration


simulator = TuringMachineSimulator(simple_machine)
if len(sys.argv) < 2:
    print("Usage: python main.py <input>")
    exit(1)

input_word = sys.argv[1]
final_state = simulator.simulate(input_word)

for configuration in simulator.get_history():
    print(render_configuration(configuration))

print(f"Final state: {final_state}")

if final_state == simple_machine.accept_state:
    print("Input accepted")
elif final_state == simple_machine.reject_state:
    print("Input rejected")
else:
    print("Machine halted")