import qiskit
import matplotlib

from algo.func_optimizer import BfgsOptimizer, CmaesOptimizer
from mutations import Weighted, Insert, Remove

matplotlib.use('Agg')

from algo.one_plus_lambda import OnePlusLambda, EvolutionReport, IterationReport
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
# mutations.add_two_block_layers(circuit, GateTypes.block_cnot)


def on_iteration_end(report: IterationReport):
    num_evaluations = sum(m.num_circ_evaluations for m in report.mutations)
    print('Iteration #{} is finished, {} circuit evaluations performed'.format(report.index, num_evaluations))
    if report.better:
        best_mutation = report.mutations[0]
        print('Better circuit found: {}'.format(best_mutation.value))


# Run evolutional algorithm
ev = OnePlusLambda(
    target=task.min_eigenvalue,
    vqe=Vqe(hamiltonian=task.H, optimizer=CmaesOptimizer(0.0016)),
    mutation=Weighted([
        (Insert(GateTypes.block_b), 1),
        (Remove(), 1)
    ]),
    initial=circuit,
    target_eps=0.0016,
    alambda=4
)
report: EvolutionReport = ev.run(iteration_end_callback=on_iteration_end)

# Show results
print('Best value is: ' + str(report.best_circuit_value))
print('Number of iterations is: ' + str(len(report.iterations)))

qk_circuit: qiskit.QuantumCircuit = QCircuitConversions.to_qiskit_circuit(report.best_circuit)
print(qk_circuit.draw(line_length=240))
print('Circuit image is saved into best_circuit.png')
qk_circuit.draw(output='mpl', filename='best_circuit.png')

