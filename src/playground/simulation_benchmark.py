from iohelper.qio import qu_load
from qutip import tensor, basis
from circuits import create_qaoa_circuit, create_random_circuit
import npq

from quantum_circuit import QuantumCircuit

N = 8
H = qu_load('H_BeH2_N=8')
H.isherm = True
psi0 = tensor(basis(2, 1), basis(2, 1), basis(2, 0), basis(2, 0), basis(2, 0), basis(2, 0), basis(2, 0),
              basis(2, 0)).unit()

npH = H.full()
npPsi0 = psi0.full().flatten()
classicPsi0 = npq.to_classic_state(npPsi0)


def benchmark_circuit(name, circuit: QuantumCircuit):
    def compute_via_qutip():
        circuit.as_operator() * psi0

    def run_statevector_simulation():
        circuit.run_qiskit_simulation()

    def run_qasm_simulation():
        circuit.run_qiskit_simulation(backend_type='qasm_simulator')

    def benchmark(name, func, max_n=100, max_time=3.0):
        import time
        start_time = time.time()
        cur_time = start_time
        n = 0
        while n < max_n and (cur_time - start_time) < max_time:
            func()
            n += 1
            cur_time = time.time()
        time_elapsed = cur_time - start_time
        print("  {}\t{:.1f} ops".format(name, n / time_elapsed))

    # print(circuit.as_qiskit_circuit().draw(line_length=240))
    print(name)
    benchmark('Qutip', compute_via_qutip)
    benchmark('Qiskit (statevector)', run_statevector_simulation)
    benchmark('Qiskit (QASM)', run_qasm_simulation)


benchmark_circuit('QAOA (1)', create_qaoa_circuit(N, classicPsi0, 1))
benchmark_circuit('QAOA (3)', create_qaoa_circuit(N, classicPsi0, 3))
benchmark_circuit('QAOA (5)', create_qaoa_circuit(N, classicPsi0, 5))
benchmark_circuit('Random', create_random_circuit(N, 20, 42, classicPsi0))
