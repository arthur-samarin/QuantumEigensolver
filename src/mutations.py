from typing import List, Tuple

from circuit import QCircuit, GateInstance, GateType, GateTypes
from random import randint, choices, sample


class Mutation:
    def apply(self, circ: QCircuit):
        raise NotImplemented()


class Remove(Mutation):
    def apply(self, circ: QCircuit):
        if circ.size > 0:
            index = randint(0, circ.size - 1)
            circ.remove_at(index)


class Insert(Mutation):
    def __init__(self, gate_type: GateType):
        self.gate_type = gate_type

    def apply(self, circ: QCircuit):
        targets = sample(range(circ.num_qubits), self.gate_type.num_qubits)
        insert_gate_into_random_place(circ, GateInstance(self.gate_type, targets))


class Weighted(Mutation):
    def __init__(self, mutations: List[Tuple[Mutation, float]]):
        self.mutations = [m[0] for m in mutations]
        self.weights = [m[1] for m in mutations]

    def apply(self, circ: QCircuit):
        mutation = choices(self.mutations, self.weights)[0]
        mutation.apply(circ)


def insert_gate_into_random_place(circ: QCircuit, gate: GateInstance):
    index = randint(0, circ.size)
    circ.insert(index, gate)


def add_two_block_layers(circ: QCircuit, block_type: GateType):
    num_qubits = circ.num_qubits
    for i in range(0, num_qubits - 1, 2):
        circ.insert(circ.size, GateInstance(block_type, [i, i + 1]))
    for i in range(1, circ.num_qubits - 1, 2):
        circ.insert(circ.size, GateInstance(block_type, [i, i + 1]))
