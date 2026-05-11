import sys
from examples.simple_machine import simple_machine
from tm.simulator import TuringMachineSimulator
from visualization.tape_renderer import render_configuration
from reduction.tableau import ComputationTableau
from reduction.encoding import TableauEncoder


simulator = TuringMachineSimulator(simple_machine)
if len(sys.argv) < 2:
    print("Usage: python main.py <input>")
    exit(1)

input_word = sys.argv[1]
final_state = simulator.simulate(input_word)

# TABLEAU PRINTING
tableau = ComputationTableau(
    simulator.get_history()
)
print("\nComputation Tableau:\n")
for row in tableau.generate_rows():
    print(row)


encoder = TableauEncoder(tableau)
print("\nSAT Variables:\n")
for variable in encoder.generate_variables():
    print(variable)
    
print("\n")
    
for configuration in simulator.get_history():
    print(render_configuration(configuration))

print(f"Final state: {final_state}")

if final_state == simple_machine.accept_state:
    print("Input accepted")
elif final_state == simple_machine.reject_state:
    print("Input rejected")
else:
    print("Machine halted")
    
    
