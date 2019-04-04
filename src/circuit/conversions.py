from circuit import QCircuit
import qutip
import npq
import qiskit as qk


class QCircuitConversions:
    @staticmethod
    def to_qobj_wavefunction(circ: QCircuit) -> qutip.Qobj:
        wavefunc = npq.np_to_ket(npq.classical_state(circ.num_qubits, circ.initial_classical_state))
        for gate in circ.gates:
            op = gate.as_large_qobj_operator(circ.num_qubits)
            wavefunc = op * wavefunc
        return wavefunc

    @staticmethod
    def to_qiskit_circuit(circ: QCircuit) -> qk.QuantumCircuit:
        reg = qk.QuantumRegister(circ.num_qubits, 'q')
        qk_circ = qk.QuantumCircuit(reg)

        initial_state = circ.initial_classical_state
        for i in range(0, circ.num_qubits):
            if (initial_state >> i) & 1 != 0:
                qk_circ.x(reg[circ.num_qubits - i - 1])

        for gate in circ.gates:
            gate.typ.to_qiskit_circuit(gate, qk_circ, reg)

        return qk_circ
