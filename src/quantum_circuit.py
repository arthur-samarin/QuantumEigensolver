import functools
import operator
import qutip
import numpy as np
import qiskit as qk
import npq
import copy
from qiskit import QuantumRegister


class QuantumCircuitPart:
    def __init__(self, N: int, num_params: int):
        self.N = N
        self.num_params = num_params

    def as_operator(self):
        pass

    def add_to_qiskit_circuit(self, circ: qk.QuantumCircuit, qreg: QuantumRegister):
        pass

    def load_parameters(self, arr, index: int):
        pass

    def store_parameters(self, arr, index: int):
        pass


class CNotEntangle(QuantumCircuitPart):
    def __init__(self, N: int):
        super().__init__(N, 0)

        cnots = [qutip.cnot(N, i, j) for i in range(0, N) for j in range(i + 1, N)]
        self._operator = functools.reduce(operator.mul, cnots)

    def as_operator(self):
        return self._operator

    def add_to_qiskit_circuit(self, circ: qk.QuantumCircuit, qreg: QuantumRegister):
        N = self.N
        for i in range(0, N):
            for j in range(i + 1, N):
                circ.cx(qreg[i], qreg[j])


class CNot(QuantumCircuitPart):
    def __init__(self, N: int, control: int, target: int):
        assert 0 <= control < N
        assert 0 <= target < N

        super().__init__(N, 0)
        self.control = control
        self.target = target

    def as_operator(self):
        return qutip.cnot(self.N, self.control, self.target)

    def add_to_qiskit_circuit(self, circ: qk.QuantumCircuit, qreg: QuantumRegister):
        circ.cx(qreg[self.control], qreg[self.target])


class RotX(QuantumCircuitPart):
    def __init__(self, N: int, target: int, angle: float):
        assert 0 <= target < N

        super().__init__(N, 1)
        self.target = target
        self.angle = angle

    def as_operator(self):
        return qutip.rx(self.angle, N = self.N, target = self.target)

    def add_to_qiskit_circuit(self, circ: qk.QuantumCircuit, qreg: QuantumRegister):
        circ.rx(self.angle, qreg[self.target])

    def load_parameters(self, arr, index: int):
        self.angle = arr[index]

    def store_parameters(self, arr, index: int):
        arr[index] = self.angle


class Not(QuantumCircuitPart):
    def __init__(self, N: int, target: int):
        assert 0 <= target < N

        super().__init__(N, 1)
        self.target = target

    def as_operator(self):
        return qutip.gate_expand_1toN(qutip.sigmax(), N = self.N, target = self.target)

    def add_to_qiskit_circuit(self, circ: qk.QuantumCircuit, qreg: QuantumRegister):
        circ.x(qreg[self.target])

    def load_parameters(self, arr, index: int):
        self.angle = arr[index]

    def store_parameters(self, arr, index: int):
        arr[index] = self.angle


class RotY(QuantumCircuitPart):
    def __init__(self, N: int, target: int, angle: float):
        assert 0 <= target < N

        super().__init__(N, 1)
        self.target = target
        self.angle = angle

    def as_operator(self):
        return qutip.ry(self.angle, N = self.N, target = self.target)

    def add_to_qiskit_circuit(self, circ: qk.QuantumCircuit, qreg: QuantumRegister):
        circ.ry(self.angle, qreg[self.target])

    def load_parameters(self, arr, index: int):
        self.angle = arr[index]

    def store_parameters(self, arr, index: int):
        arr[index] = self.angle


class RotZ(QuantumCircuitPart):
    def __init__(self, N: int, target: int, angle: float):
        assert 0 <= target < N

        super().__init__(N, 1)
        self.target = target
        self.angle = angle

    def as_operator(self):
        return qutip.phasegate(self.angle, N = self.N, target = self.target)

    def add_to_qiskit_circuit(self, circ: qk.QuantumCircuit, qreg: QuantumRegister):
        circ.rz(self.angle, qreg[self.target])

    def load_parameters(self, arr, index: int):
        self.angle = arr[index]

    def store_parameters(self, arr, index: int):
        arr[index] = self.angle


class Static(QuantumCircuitPart):
    def __init__(self, part: QuantumCircuitPart):
        super().__init__(part.N, 0)
        self.part = part

    def as_operator(self):
        return self.part.as_operator()

    def add_to_qiskit_circuit(self, circ: qk.QuantumCircuit, qreg: QuantumRegister):
        self.part.add_to_qiskit_circuit(circ, qreg)


class QuantumCircuit:
    def __init__(self, N: int, parts = None):
        self._parts = parts or []
        self.N = N

        for part in self._parts:
            assert part.N == self.N

    def as_operator(self):
        if self.size > 0:
            matrices = [p.as_operator() for p in self._parts]
            return functools.reduce(operator.mul, reversed(matrices))
        else:
            return qutip.rx(0, N = self.N, target=0)

    def as_qiskit_circuit(self, initial_state = None):
        qubits = qk.QuantumRegister(self.N, 'q')
        circ = qk.QuantumCircuit(qubits)

        if initial_state is not None:
            # State indices in Qutip and in Qiskit are based on different orders of qubits
            circ.initialize(npq.reverse_qubits_in_state(initial_state), qubits)

        for gate in self._parts:
            gate.add_to_qiskit_circuit(circ, qubits)

        return circ

    def apply_to_state(self, initial_state):
        circ = self.as_qiskit_circuit(initial_state)
        backend_sim = qk.BasicAer.get_backend('statevector_simulator')
        result = qk.execute(circ, backend_sim).result()
        state = result.get_statevector(circ)
        return npq.reverse_qubits_in_state(np.array(state))

    def store_parameters(self, arr: np.ndarray):
        assert arr.shape[0] == self.num_parameters

        i = 0
        for p in self._parts:
            p.store_parameters(arr, i)
            i += p.num_params

    def load_parameters(self, arr: np.ndarray):
        assert arr.shape[0] == self.num_parameters

        i = 0
        for p in self._parts:
            p.load_parameters(arr, i)
            i += p.num_params

    @property
    def num_parameters(self):
        if self.size == 0:
            return 0
        v = functools.reduce(operator.add, map(lambda part: part.num_params, self._parts))
        return v

    @property
    def size(self):
        return len(self._parts)

    def insert(self, index: int, gate: QuantumCircuitPart):
        assert gate.N == self.N
        assert 0 <= index <= self.size
        self._parts.insert(index, gate)

    def remove_at(self, index: int):
        assert 0 <= index < self.size
        self._parts.pop(index)

    def clone(self):
        new_schema = QuantumCircuit(self.N)
        new_schema._parts = copy.deepcopy(self._parts)
        return new_schema
