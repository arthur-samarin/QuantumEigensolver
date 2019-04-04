import qiskit
import matplotlib

from algo.func_optimizer import BfgsOptimizer, CmaesOptimizer

matplotlib.use('Agg')

from algo.one_plus_lambda import OnePlusLambda
from iohelper import hamiltonians
import mutations
from circuit import QCircuit, GateTypes, QCircuitConversions
from algo.vqe import Vqe

task = hamiltonians.q4

# Show information about task
print('Minimal eigenvalue is  {}'.format(task.min_eigenvalue))
print('Initial state is {}'.format(task.classical_psi0_bitstring))

# Initialize circuit with something random
circuit = QCircuit(task.N, task.classical_psi0, [])
mutations.add_two_block_layers(circuit, GateTypes.block_cnot)

# Run evolutional algorithm
ev = OnePlusLambda(
    target=task.min_eigenvalue,
    vqe=Vqe(hamiltonian=task.H, optimizer=CmaesOptimizer(0.0016)),
    mutate=mutations.random_block_mutation,
    initial=circuit,
    target_eps=0.0016,
    alambda=12
)
ev.run()

# Show results
print('Best value is: ' + str(ev.best_result.opt_value))
print('Number of iterations is: ' + str(ev.num_iterations))

qk_circuit: qiskit.QuantumCircuit = QCircuitConversions.to_qiskit_circuit(ev.best_result.circ)
print(qk_circuit.draw(line_length=240))
print('Circuit image is saved into best_circuit.png')
qk_circuit.draw(output='mpl', filename='best_circuit.png')

