from circuit import QCircuit, GateInstance, GateType, GateTypes
from random import randint, choice, sample


def insert_gate_into_random_place(circ: QCircuit, gate: GateInstance):
    index = randint(0, circ.size)
    circ.insert(index, gate)


def insert_gate_type_into_random_place(gate_type: GateType):
    def mutator(circ: QCircuit):
        targets = sample(range(circ.num_qubits), gate_type.num_qubits)
        insert_gate_into_random_place(circ, GateInstance(gate_type, targets))
    return mutator


def delete_random_element(circ: QCircuit):
    if circ.size > 0:
        index = randint(0, circ.size - 1)
        circ.remove_at(index)


def random_block_mutation(circ: QCircuit):
    mutators = [
        insert_gate_type_into_random_place(GateTypes.block_cnot),
        insert_gate_type_into_random_place(GateTypes.block_sqrtswap),
        delete_random_element
    ]
    mutator = choice(mutators)
    mutator(circ)


def add_two_block_layers(circ: QCircuit, block_type: GateType):
    num_qubits = circ.num_qubits
    for i in range(0, num_qubits - 1, 2):
        circ.insert(circ.size, GateInstance(block_type, [i, i + 1]))
    for i in range(1, circ.num_qubits - 1, 2):
        circ.insert(circ.size, GateInstance(block_type, [i, i + 1]))
