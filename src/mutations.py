from quantum_circuit import QuantumCircuit, CNot, RotX, RotZ, QuantumCircuitPart
from random import randint, choice


def insert_into_random_place(schema: QuantumCircuit, gate: QuantumCircuitPart):
    index = randint(0, schema.size)
    schema.insert(index, gate)


def insert_random_cnot(schema: QuantumCircuit):
    control = randint(0, schema.N - 1)
    while True:
        target = randint(0, schema.N - 1)
        if target != control:
            break

    insert_into_random_place(schema, CNot(schema.N, control, target))


def insert_random_rx(schema: QuantumCircuit):
    target = randint(0, schema.N - 1)
    insert_into_random_place(schema, RotX(schema.N, target, 0))


def insert_random_rz(schema: QuantumCircuit):
    target = randint(0, schema.N - 1)
    insert_into_random_place(schema, RotZ(schema.N, target, 0))


def delete_random_element(schema: QuantumCircuit):
    if schema.size > 0:
        index = randint(0, schema.size - 1)
        schema.remove_at(index)


def random_mutation(schema: QuantumCircuit):
    mutators = [insert_random_cnot, insert_random_rx, insert_random_rz, delete_random_element]
    mutator = choice(mutators)
    mutator(schema)
