from quantum_circuit import RotX, RotY, RotZ, CNot, Static, QuantumCircuit, CNotEntangle
import numpy as np


def create_qaoa_circuit(N, initial_state, p):
    parts = []

    # X rotation
    for i in range(0, N):
        parts.append(RotX(N, i, 0))

    for j in range(0, p):
        # Entangle
        parts.append(CNotEntangle(N))

        # X rotations
        for i in range(0, N):
            parts.append(RotX(N, i, 0))

        # Z rotations
        for i in range(0, N):
            parts.append(RotZ(N, i, 0))

    return QuantumCircuit(N, initial_state, parts)


def create_random_circuit(N, num_mutations, seed, initial_state):
    import mutations
    circ = QuantumCircuit(N, initial_state)
    for i in range(num_mutations):
        mutations.random_mutation(circ)
    return circ
