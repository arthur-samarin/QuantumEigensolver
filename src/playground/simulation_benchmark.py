from algo.func_optimizer import BfgsOptimizer, CmaesOptimizer, Optimizer
from circuit import QCircuit, QCircuitConversions, GateTypes, GateInstance
import qiskit as qk
import mutations
import random
import npq
import numpy as np
import qutip
import time
from iohelper import hamiltonians


def benchmark(name, func, max_n=1000, max_time=3.0):
    start_time = time.time()
    cur_time = start_time
    n = 0
    while n < max_n and (cur_time - start_time) < max_time:
        func()
        n += 1
        cur_time = time.time()
    time_elapsed = cur_time - start_time
    print("  {}\t{:.3f}".format(name, n / time_elapsed))


def benchmark_circuit(name, circ: QCircuit):
    qk_circuit = QCircuitConversions.to_qiskit_circuit(circ)
    qk_backend = qk.BasicAer.get_backend('statevector_simulator')

    def compute_via_quest():
        w = QCircuitConversions.to_qobj_wavefunction(circ)
        return w

    def compute_via_qutip():
        wavefunc = npq.np_to_ket(npq.classical_state(circ.num_qubits, circ.initial_classical_state))
        for gate in circ.gates:
            op = gate.as_large_qobj_operator(circ.num_qubits)
            wavefunc = op * wavefunc
        return wavefunc

    def compute_via_qiskit():
        result = qk.execute(qk_circuit, qk_backend).result()
        state = result.get_statevector(qk_circuit)
        return npq.np_to_ket(npq.reverse_qubits_in_state(np.array(state)))

    def check_equality():
        q1 = npq.qobj_to_np(compute_via_quest())
        q2 = npq.qobj_to_np(compute_via_qutip())
        q3 = npq.qobj_to_np(compute_via_qiskit())
        assert np.allclose(q1, q2)
        assert np.allclose(q1, q3)

    def benchmark_vqe(name: str, optimizer: Optimizer, wavefunction_calc_func, H):
        num_evaluations = [0]

        def func_to_minimize(params):
            num_evaluations[0] += 1
            circ.set_parameters(params)
            return qutip.expect(H, wavefunction_calc_func())

        def vqe_func():
            bounds = circ.parameters_bounds
            circ.reset_parameters()
            optimizer.optimize(func_to_minimize, circ.get_parameters(), bounds)

        start = time.time()
        vqe_func()
        end = time.time()
        print('  {}'.format(name))
        print('    Evaluations/s: {:.3f}'.format(1.0 * num_evaluations[0] / (end - start)))
        print('    Optimizations/s: {:.3f}'.format(1.0 / (end - start)))


    check_equality()

    # print(qk_circuit.draw(line_length=240))
    print(name)

    task = hamiltonians.for_qubits(circ.num_qubits)
    if task:
        H = task.H
        benchmark_vqe('Vqe (bfgs, QuEST)', BfgsOptimizer(), compute_via_quest, H)
        benchmark_vqe('Vqe (CMA-ES, QuEST)', CmaesOptimizer(0.0016), compute_via_quest, H)
        benchmark_vqe('Vqe (bfgs, Qutip)', BfgsOptimizer(), compute_via_qutip, H)
        benchmark_vqe('Vqe (CMA-ES, Qutip)', CmaesOptimizer(0.0016), compute_via_qutip, H)

    benchmark('Evaluations/s (QuEST)', compute_via_quest)
    benchmark('Evaluations/s (Qutip)', compute_via_qutip)
    benchmark('Evaluations/s (Qiskit (statevector))', compute_via_qiskit)


def create_random_block_circuit(num_qubits: int, size: int, initial_state=0):
    circ = QCircuit(num_qubits, initial_state, [])
    for _ in range(size):
        gate_type = random.choice([GateTypes.block_a])
        mutations.Insert(gate_type).apply(circ)
    return circ


def create_random_circuit(num_qubits: int, num_cnots: int, num_rx: int, initial_state=0):
    circ = QCircuit(num_qubits, initial_state, [])
    for _ in range(num_cnots):
        mutations.Insert(GateTypes.cnot).apply(circ)
    for _ in range(num_rx):
        mutations.Insert(GateTypes.rx).apply(circ)
    return circ


def main():
    num_qubits = 4
    size = 4
    benchmark_circuit('Random with Block-A (size={})'.format(size), create_random_block_circuit(num_qubits, size, initial_state=0b1100))
    benchmark_circuit('Random with CNOT and RX (1:8) (size={})'.format(size * 9), create_random_circuit(num_qubits, size, size * 8, initial_state=0b1100))


if __name__ == '__main__':
    main()
