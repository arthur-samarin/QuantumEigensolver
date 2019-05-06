import functools
import operator
from typing import List, Tuple, Optional, Union

import numpy as np
import qutip
import qiskit as qk

from quest import QuestOps, Qureg


class QCircuit:
    def __init__(self, num_qubits: int, initial_classical_state: int, gates: List["GateInstance"]):
        self.num_qubits = num_qubits
        self.initial_classical_state = initial_classical_state
        self.gates = list(gates)

    @property
    def num_parameters(self):
        if self.size == 0:
            return 0
        return functools.reduce(operator.add, map(lambda gate: gate.typ.num_params, self.gates))

    def set_parameters(self, arr: np.ndarray) -> None:
        if len(arr) != self.num_parameters:
            raise ValueError('Bad parameters length: {} expected, {} actual'.format(self.num_parameters, len(arr)))

        i = 0
        for gate in self.gates:
            gate.params[:] = arr[i:i+gate.typ.num_params]
            i += gate.typ.num_params

    def get_parameters(self) -> np.ndarray:
        p = np.zeros(self.num_parameters)
        i = 0
        for gate in self.gates:
            p[i:i + gate.typ.num_params] = gate.params
            i += gate.typ.num_params
        return p

    def reset_parameters(self) -> None:
        for gate in self.gates:
            gate.reset_parameters()

    @property
    def parameters_bounds(self):
        bounds = []
        for gate in self.gates:
            ranges = gate.typ.param_ranges
            for range in ranges:
                bounds.append(range)
        return bounds

    @property
    def size(self):
        return len(self.gates)

    def insert(self, index: int, gate: "GateInstance"):
        assert 0 <= index <= self.size
        self.gates.insert(index, gate)

    def remove_at(self, index: int):
        assert 0 <= index < self.size
        self.gates.pop(index)

    def clone(self) -> "QCircuit":
        return QCircuit(self.num_qubits, self.initial_classical_state, [gate.clone() for gate in self.gates])


class GateType:
    def __init__(self, name: str, num_qubits: int, num_params: int, param_ranges: List[Tuple[Optional[float], Optional[float]]]):
        self.name = name
        self.num_qubits = num_qubits
        self.num_params = num_params
        self.param_ranges = param_ranges

        assert len(self.param_ranges) == self.num_params

    def as_qobj_operator(self, instance: "GateInstance") -> qutip.Qobj:
        raise NotImplemented()

    def to_qiskit_circuit(self, instance: "GateInstance", circ: qk.QuantumCircuit, reg: qk.QuantumRegister) -> None:
        raise NotImplemented()

    def add_to_cvqe(self, instance: "GateInstance", c, gt):
        raise NotImplemented()


    def execute_on_quest_qureg(self, qureg: Qureg, instance: "GateInstance"):
        raise NotImplemented()

    def reset_parameters(self, instance: "GateInstance"):
        instance.params = np.array([np.random.uniform(bottom, top) for bottom, top in self.param_ranges])


class GateInstance:
    def __init__(self, typ: GateType, qubits: List[int], params: Union[np.ndarray, List[float]] = None):
        self.typ = typ
        self.qubits = list(qubits)
        self.params = np.zeros(typ.num_params)

        if len(set(qubits)) != len(qubits):
            raise ValueError('Qubits must be unique')
        if len(qubits) != typ.num_qubits:
            raise ValueError('Bad length of list of qubits')
        if params is not None:
            if len(params) != len(self.params):
                raise ValueError('Bad length of params, expected {}, actual {}'.format(typ.num_params, len(params)))
            self.params[:] = params

    def as_qobj_operator(self) -> qutip.Qobj:
        return self.typ.as_qobj_operator(self)

    def as_large_qobj_operator(self, num_qubits: int) -> qutip.Qobj:
        if self.typ.num_qubits == 2:
            return qutip.gate_expand_2toN(self.as_qobj_operator(), num_qubits, targets=self.qubits)
        elif self.typ.num_qubits == 1:
            return qutip.gate_expand_1toN(self.as_qobj_operator(), num_qubits, self.qubits[0])
        else:
            raise NotImplemented('Not implemented for large gates')

    def reset_parameters(self):
        self.typ.reset_parameters(self)

    def clone(self) -> "GateInstance":
        return GateInstance(self.typ, self.qubits, self.params)
