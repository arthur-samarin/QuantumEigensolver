import functools
import operator
import qutip
import numpy as np


class QuantumCircuitPart:
    def __init__(self, N: int, num_params: int):
        self.N = N
        self.num_params = num_params

    def as_operator(self):
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


class CNot(QuantumCircuitPart):
    def __init__(self, N: int, control: int, target: int):
        assert 0 <= control < N
        assert 0 <= target < N

        super().__init__(N, 0)
        self.control = control
        self.target = target

    def as_operator(self):
        return qutip.cnot(self.N, self.control, self.target)


class RotX(QuantumCircuitPart):
    def __init__(self, N: int, target: int, angle: float):
        assert 0 <= target < N

        super().__init__(N, 1)
        self.target = target
        self.angle = angle

    def as_operator(self):
        return qutip.rx(self.angle, N = self.N, target = self.target)

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
        return qutip.rz(self.angle, N = self.N, target = self.target)

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


class Reverse(QuantumCircuitPart):
    def __init__(self, N: int, target: int):
        assert 0 <= target < N

        super().__init__(N, 0)
        self.target = target

    def as_operator(self):
        return qutip.gate_expand_1toN(-qutip.qeye(2), self.N, self.target)


class QuantumCircuit:
    def __init__(self, N: int, parts = None):
        self._parts = parts or []
        self.N = N

        for part in self._parts:
            assert part.N == self.N

    def as_operator(self):
        if self.size > 0:
            matrices = [p.as_operator() for p in self._parts]
            return functools.reduce(operator.mul, matrices)
        else:
            return qutip.rx(0, N = self.N, target=0)

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
        new_schema._parts = list(self._parts)
        return new_schema
