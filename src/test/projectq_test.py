from quantum_circuit import RotX, RotY, RotZ, CNot, QuantumCircuit, Not
from npq import classic_states, np_to_ket, qobj_to_np
import numpy as np
import unittest
import random


class ComputationTests(unittest.TestCase):
    """
    Tests that computations via Qutip and ProjectQ give the same result
    """

    def test_2(self):
        N = 2
        operators = [
            [Not(N, i) for i in range(0, N)],
            [RotX(N, i, np.pi) for i in range(0, N)],
            [RotY(N, i, np.pi) for i in range(0, N)],
            [RotZ(N, i, np.pi) for i in range(0, N)],
            [CNot(N, i, j) for i in range(0, N) for j in range(i + 1, N)]
        ]
        operators = [op for op_list in operators for op in op_list]

        for i in range(0, 100):
            for initial_state in classic_states(N):
                circuit = QuantumCircuit(N, [operators[random.randint(0, len(operators) - 1)] for i in range(0, 2)])

                initial_state_ket = np_to_ket(initial_state)

                qutip_operator = circuit.as_operator()
                new_state_via_qutip = qobj_to_np(qutip_operator * initial_state_ket)
                new_state_via_qiskit = circuit.apply_to_state(initial_state)

                if not np.allclose(new_state_via_qutip, new_state_via_qiskit):
                    print(circuit.as_qiskit_circuit(initial_state).draw())
                    print('Initial: {}',format(initial_state))
                    print('Result (Qutip): {}'.format(new_state_via_qutip))
                    print('Result (Qiskit): {}'.format(new_state_via_qiskit))
                    print('Delta: {}'.format(new_state_via_qiskit - new_state_via_qutip))
                    print('|Delta|: {}'.format(np.max(np.abs(new_state_via_qiskit - new_state_via_qutip))))
                    assert False
