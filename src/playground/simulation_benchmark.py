from circuit import QCircuit, QCircuitConversions, GateTypes
import qiskit as qk
import mutations
import random
import npq
import numpy as np


def benchmark_circuit(name, circ: QCircuit):
    qk_circuit = QCircuitConversions.to_qiskit_circuit(circ)
    qk_backend = qk.BasicAer.get_backend('statevector_simulator')

    def compute_via_qutip():
        wavefunc = npq.np_to_ket(npq.classical_state(circ.num_qubits, circ.initial_classical_state))
        for gate in circ.gates:
            op = gate.as_large_qobj_operator(circ.num_qubits)
            wavefunc = op * wavefunc
        return wavefunc

    def compute_via_qiskit():
        result = qk.execute(qk_circuit, qk_backend).result()
        state = result.get_statevector(qk_circuit)
        return npq.reverse_qubits_in_state(np.array(state))

    def check_equality():
        q1 = npq.qobj_to_np(compute_via_qutip())
        q2 = compute_via_qiskit()
        assert np.allclose(q1, q2)

    check_equality()

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
        print("  {}\t{:.3f} ops".format(name, n / time_elapsed))

    print(qk_circuit.draw(line_length=240))
    print(name)
    benchmark('Qutip', compute_via_qutip)
    benchmark('Qiskit (statevector)', compute_via_qiskit)


def create_random_circuit(num_qubits: int, num_rotations: int, num_cnots: int):
    circ = QCircuit(num_qubits, 0, [])
    for _ in range(num_rotations):
        gate_type = random.choice([GateTypes.rx, GateTypes.ry, GateTypes.rz])
        mutations.Insert(gate_type).apply(circ)
    for _ in range(num_cnots):
        gate_type = random.choice([GateTypes.cnot])
        mutations.Insert(gate_type).apply(circ)
    return circ


def main():
    num_qubits = 4
    size = 20
    num_rotations = size * 3 // 4
    num_cnots = size // 4
    benchmark_circuit('Random (size={})'.format(size), create_random_circuit(num_qubits, num_rotations, num_cnots))


if __name__ == '__main__':
    main()
