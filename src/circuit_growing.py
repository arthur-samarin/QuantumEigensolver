import qiskit
import matplotlib
matplotlib.use('Agg')

from algo.one_plus_lambda import OnePlusLambda
from iohelper import hamiltonians
import mutations
from quantum_circuit import QuantumCircuit
from algo.vqe import Vqe

task = hamiltonians.q4

# Show information about task
print('Minimal eigenvalue is  {}'.format(task.min_eigenvalue))
print('Initial state is {}'.format(task.classical_psi0_bitstring))

# Initialize circuit with something random
circuit = QuantumCircuit(task.N, task.classical_psi0)
mutations.add_two_block_layers(circuit)

# Run evolutional algorithm
vqe = Vqe(task.H)
ev = OnePlusLambda(
    target=task.min_eigenvalue,
    evaluate=vqe.optimize,
    mutate=mutations.random_block_mutation,
    initial=circuit,
    target_eps=0.0016,
    alambda=12
)
ev.run()

# Show results
print('Best value is: ' + str(ev.best_score))
print('Number of iterations is: ' + str(ev.num_iterations))

qk_circuit: qiskit.QuantumCircuit = ev.best_circuit.as_qiskit_circuit()
print(qk_circuit.draw(line_length=240))
print('Circuit image is saved into best_circuit.png')
qk_circuit.draw(output='mpl', filename='best_circuit.png')

