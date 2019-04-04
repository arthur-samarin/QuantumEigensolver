from typing import List, Tuple

import qiskit as qk

from circuit.architecture import GateType, GateInstance
import qutip
import numpy as np


class RxGateType(GateType):
    def __init__(self, name):
        super().__init__(name, 1, 1, [(0, np.pi)])

    def as_qobj_operator(self, instance: "GateInstance") -> qutip.Qobj:
        return qutip.rx(instance.params[0])

    def to_qiskit_circuit(self, instance: "GateInstance", circ: qk.QuantumCircuit, reg: qk.QuantumRegister) -> None:
        circ.rx(instance.params[0], reg[instance.qubits[0]])


class RzGateType(GateType):
    def __init__(self, name):
        super().__init__(name, 1, 1, [(0, np.pi)])

    def as_qobj_operator(self, instance: "GateInstance") -> qutip.Qobj:
        return qutip.phasegate(instance.params[0])

    def to_qiskit_circuit(self, instance: "GateInstance", circ: qk.QuantumCircuit, reg: qk.QuantumRegister) -> None:
        circ.rz(instance.params[0], reg[instance.qubits[0]])


class CNotGateType(GateType):
    def __init__(self, name):
        super().__init__(name, 2, 0, [])

    def as_qobj_operator(self, instance: "GateInstance") -> qutip.Qobj:
        return qutip.cnot()

    def to_qiskit_circuit(self, instance: "GateInstance", circ: qk.QuantumCircuit, reg: qk.QuantumRegister) -> None:
        circ.cx(reg[instance.qubits[0]], reg[instance.qubits[1]])


class SqrtswapGateType(GateType):
    def __init__(self, name):
        super().__init__(name, 2, 0, [])

    def as_qobj_operator(self, instance: "GateInstance") -> qutip.Qobj:
        return qutip.sqrtswap()

    def to_qiskit_circuit(self, instance: "GateInstance", circ: qk.QuantumCircuit, reg: qk.QuantumRegister) -> None:
        circ.swap(reg[instance.qubits[0]], reg[instance.qubits[1]])


class CombinedGateType(GateType):
    def __init__(self, name, num_qubits, gate_placements: List[Tuple[GateType, List[int]]]):
        num_params = sum(map(lambda g: g[0].num_params, gate_placements))
        param_ranges = [bounds for gate_type, targets in gate_placements for bounds in gate_type.param_ranges]

        super().__init__(name, num_qubits, num_params, param_ranges)
        self.gate_placements = gate_placements

    def as_qobj_operator(self, instance: "GateInstance") -> qutip.Qobj:
        op = qutip.rx(0, self.num_qubits, 0)
        i = 0
        for gate_type, targets in self.gate_placements:
            fake_instance = GateInstance(gate_type, targets, instance.params[i:i + gate_type.num_params])
            op = self._expand_gate(gate_type.as_qobj_operator(fake_instance), gate_type.num_qubits, self.num_qubits, targets) * op
            i += gate_type.num_params
        return op

    def to_qiskit_circuit(self, instance: "GateInstance", circ: qk.QuantumCircuit, reg: qk.QuantumRegister) -> None:
        regs = [reg[q] for q in instance.qubits]
        i = 0
        for gate_type, targets in self.gate_placements:
            fake_instance = GateInstance(gate_type, targets, instance.params[i:i + gate_type.num_params])
            gate_type.to_qiskit_circuit(fake_instance, circ, regs)
            i += gate_type.num_params

    @staticmethod
    def _expand_gate(op: qutip.Qobj, from_qubits: int, to_qubits: int, targets: List[int]):
        assert len(targets) == from_qubits

        if from_qubits == 1:
            return qutip.gate_expand_1toN(op, to_qubits, targets[0])
        elif from_qubits == 2:
            return qutip.gate_expand_2toN(op, to_qubits, targets=targets)
        else:
            raise ValueError('Unsupported from_qubits value')


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


class GateTypes:
    rx = RxGateType('rx')
    rz = RzGateType('rz')
    cnot = CNotGateType('cnot')
    sqrtswap = SqrtswapGateType('sqrtswap')
    block_cnot = BlockGateType('block-cnot', rx, rz, cnot)
    block_sqrtswap = BlockGateType('block-sqrtswap', rx, rz, sqrtswap)
    all = [
        rx,
        rz,
        cnot,
        sqrtswap,
        block_cnot,
        block_sqrtswap
    ]

    @staticmethod
    def by_name(name: str) -> GateType:
        return next(filter(lambda t: t.name == name, GateTypes.all))
