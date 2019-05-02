from typing import List, Tuple

import qiskit as qk

from circuit.architecture import GateType, GateInstance
import qutip
import numpy as np

from quest import Qureg, QuestOps


class RxGateType(GateType):
    def __init__(self, name):
        super().__init__(name, 1, 1, [(-np.pi, np.pi)])

    def as_qobj_operator(self, instance: "GateInstance") -> qutip.Qobj:
        return qutip.rx(instance.params[0])

    def to_qiskit_circuit(self, instance: "GateInstance", circ: qk.QuantumCircuit, reg: qk.QuantumRegister) -> None:
        circ.rx(instance.params[0], reg[instance.qubits[0]])

    def execute_on_quest_qureg(self, qureg: Qureg, instance: "GateInstance") -> None:
        QuestOps.rx(qureg, instance.qubits[0], instance.params[0])


class RyGateType(GateType):
    def __init__(self, name):
        super().__init__(name, 1, 1, [(-np.pi, np.pi)])

    def as_qobj_operator(self, instance: "GateInstance") -> qutip.Qobj:
        return qutip.ry(instance.params[0])

    def to_qiskit_circuit(self, instance: "GateInstance", circ: qk.QuantumCircuit, reg: qk.QuantumRegister) -> None:
        circ.ry(instance.params[0], reg[instance.qubits[0]])

    def execute_on_quest_qureg(self, qureg: Qureg, instance: "GateInstance") -> None:
        QuestOps.ry(qureg, instance.qubits[0], instance.params[0])


class RzGateType(GateType):
    def __init__(self, name):
        super().__init__(name, 1, 1, [(-np.pi, np.pi)])

    def as_qobj_operator(self, instance: "GateInstance") -> qutip.Qobj:
        return qutip.phasegate(instance.params[0])

    def to_qiskit_circuit(self, instance: "GateInstance", circ: qk.QuantumCircuit, reg: qk.QuantumRegister) -> None:
        circ.rz(instance.params[0], reg[instance.qubits[0]])

    def execute_on_quest_qureg(self, qureg: Qureg, instance: "GateInstance") -> None:
        QuestOps.rz(qureg, instance.qubits[0], instance.params[0])


class CNotGateType(GateType):
    def __init__(self, name):
        super().__init__(name, 2, 0, [])

    def as_qobj_operator(self, instance: "GateInstance") -> qutip.Qobj:
        return qutip.cnot()

    def to_qiskit_circuit(self, instance: "GateInstance", circ: qk.QuantumCircuit, reg: qk.QuantumRegister) -> None:
        circ.cx(reg[instance.qubits[0]], reg[instance.qubits[1]])

    def execute_on_quest_qureg(self, qureg: Qureg, instance: "GateInstance") -> None:
        QuestOps.cnot(qureg, instance.qubits[0], instance.qubits[1])


class SqrtswapGateType(GateType):
    def __init__(self, name):
        super().__init__(name, 2, 0, [])

    def as_qobj_operator(self, instance: "GateInstance") -> qutip.Qobj:
        return qutip.sqrtswap()

    def to_qiskit_circuit(self, instance: "GateInstance", circ: qk.QuantumCircuit, reg: qk.QuantumRegister) -> None:
        circ.swap(reg[instance.qubits[0]], reg[instance.qubits[1]])


class CombinedGateType(GateType):
    def __init__(self, name, num_qubits, gate_placements: List[Tuple[GateType, List[int]]], num_params=None, param_ranges=None):
        num_params = num_params or sum(map(lambda g: g[0].num_params, gate_placements))
        param_ranges = param_ranges or [bounds for gate_type, targets in gate_placements for bounds in gate_type.param_ranges]

        super().__init__(name, num_qubits, num_params, param_ranges)
        self.gate_placements = gate_placements

    def decompose_params(self, p: np.ndarray):
        return p

    def as_qobj_operator(self, instance: "GateInstance") -> qutip.Qobj:
        p = self.decompose_params(instance.params)
        op = qutip.rx(0, self.num_qubits, 0)
        i = 0
        for gate_type, targets in self.gate_placements:
            fake_instance = GateInstance(gate_type, targets, p[i:i + gate_type.num_params])
            op = self._expand_gate(gate_type.as_qobj_operator(fake_instance), gate_type.num_qubits, self.num_qubits, targets) * op
            i += gate_type.num_params
        return op

    def to_qiskit_circuit(self, instance: "GateInstance", circ: qk.QuantumCircuit, reg: qk.QuantumRegister) -> None:
        for q in self._decompose(instance):
            q.typ.to_qiskit_circuit(q, circ, reg)

    @staticmethod
    def _expand_gate(op: qutip.Qobj, from_qubits: int, to_qubits: int, targets: List[int]):
        assert len(targets) == from_qubits

        if from_qubits == 1:
            return qutip.gate_expand_1toN(op, to_qubits, targets[0])
        elif from_qubits == 2:
            return qutip.gate_expand_2toN(op, to_qubits, targets=targets)
        else:
            raise ValueError('Unsupported from_qubits value')

    def execute_on_quest_qureg(self, qureg: Qureg, instance: "GateInstance") -> None:
        for q in self._decompose(instance):
            q.typ.execute_on_quest_qureg(qureg, q)

    def _decompose(self, instance: GateInstance) -> List[GateInstance]:
        p = self.decompose_params(instance.params)
        instances = []
        i = 0
        for gate_type, relative_qubits in self.gate_placements:
            abs_qubits = [instance.qubits[i] for i in relative_qubits]
            instances.append(GateInstance(gate_type, abs_qubits, p[i:i + gate_type.num_params]))
            i += gate_type.num_params
        return instances


class BlockGateType(CombinedGateType):
    def __init__(self, name, rx: GateType, rz: GateType, block_type: GateType):
        super().__init__(name, 2, [
            (rx, [0]),
            (rz, [0]),
            (rx, [1]),
            (rz, [1]),
            (block_type, [0, 1]),
            (rx, [0]),
            (rz, [0]),
            (rx, [1]),
            (rz, [1]),
        ])
        self.block_type = block_type


class BlockAGateType(CombinedGateType):
    def __init__(self, name):
        super().__init__(name, 2, [
            (GateTypes.rz, [0]),
            (GateTypes.ry, [0]),
            (GateTypes.rx, [1]),
            (GateTypes.ry, [1]),
            (GateTypes.cnot, [0, 1]),
            (GateTypes.ry, [0]),
            (GateTypes.rz, [0]),
            (GateTypes.ry, [1]),
            (GateTypes.rx, [1])
        ], num_params=4, param_ranges=[(-np.pi, np.pi) for _ in range(4)])

    def decompose_params(self, p: np.ndarray):
        return np.array([p[0], p[1], p[2], p[3], -p[1], -p[0], -p[3], -p[2]])


class BlockBGateType(CombinedGateType):
    def __init__(self, name):
        super().__init__(name, 2, [
            (GateTypes.rz, [0]),
            (GateTypes.ry, [0]),
            (GateTypes.rz, [1]),
            (GateTypes.ry, [1]),
            (GateTypes.cnot, [0, 1]),
            (GateTypes.ry, [1]),
            (GateTypes.rz, [1]),
            (GateTypes.cnot, [0, 1]),
            (GateTypes.ry, [0]),
            (GateTypes.rz, [0]),
            (GateTypes.rz, [1])
        ], num_params=5, param_ranges=[(-np.pi, np.pi) for _ in range(5)])

    def decompose_params(self, p: np.ndarray):
        return np.array([p[0], p[1], p[2], p[3], -p[3], (-p[4] - p[2])/2, -p[1], -p[0], (p[4] - p[2])/2])

    def reset_parameters(self, instance: "GateInstance"):
        instance.params = np.random.uniform(-np.pi, np.pi, 5)
        instance.params[3] = np.pi
        instance.params[4] = 2*np.pi - instance.params[2]
        if instance.params[4] > np.pi:
            instance.params[4] -= 2*np.pi


class GateTypes:
    @staticmethod
    def by_name(name: str) -> GateType:
        return next(filter(lambda t: t.name == name, GateTypes.all))


GateTypes.rx = RxGateType('rx')
GateTypes.ry = RyGateType('ry')
GateTypes.rz = RzGateType('rz')
GateTypes.cnot = CNotGateType('cnot')
GateTypes.sqrtswap = SqrtswapGateType('sqrtswap')
GateTypes.block_cnot = BlockGateType('block-cnot', GateTypes.rx, GateTypes.rz, GateTypes.cnot)
GateTypes.block_sqrtswap = BlockGateType('block-sqrtswap', GateTypes.rx, GateTypes.rz, GateTypes.sqrtswap)
GateTypes.block_a = BlockAGateType('block-a')
GateTypes.block_b = BlockBGateType('block-b')

GateTypes.all = [
    GateTypes.rx,
    GateTypes.ry,
    GateTypes.rz,
    GateTypes.cnot,
    GateTypes.sqrtswap,
    GateTypes.block_cnot,
    GateTypes.block_sqrtswap,
    GateTypes.block_a,
    GateTypes.block_b
]
