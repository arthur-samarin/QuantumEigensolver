from circuits import create_qaoa_circuit
from iohelper import hamiltonians
import mutations
from algo.one_plus_one import OnePlusOne
from quantum_circuit import QuantumCircuit
from algo.vqe import Vqe

task = hamiltonians.q4

# Show information about task
print('Minimal eigenvalue is  {}'.format(task.min_eigenvalue))
print('Initial state is {}'.format(task.classical_psi0_bitstring))

# Initialize circuit with something random
circuit = QuantumCircuit(task.N, 0)
mutations.add_two_block_layers(circuit)

# Run evolutional algorithm
vqe = Vqe(task.H)
ev = OnePlusOne(
    target=task.min_eigenvalue-100,
    evaluate=vqe.optimize,
    mutate=mutations.random_block_mutation,
    initial=circuit,
    target_eps=0.0016
)
ev.run()

# Show results
print('Best value is: ' + str(ev.best_score))
print('Number of iterations is {}'.format(vqe.num_optimizations))
print('Number of circuit evaluations is {}'.format(vqe.num_circuit_evaluations))
print(ev.best_circuit.as_qiskit_circuit().draw(line_length=240))
