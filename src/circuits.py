from quantum_circuit import RotX, RotY, RotZ, CNot, Reverse, Static, QuantumCircuit, CNotEntangle
import numpy as np


def create_google_prx_schema(theta: float):
    N = 2
    parts = [
        Static(RotY(N, 0, np.pi / 2)),
        Static(RotX(N, 1, np.pi / 2)),
        Static(Reverse(N, 1)),
        Static(CNot(N, 0, 1)),
        RotZ(N, 1, theta),
        Static(CNot(N, 0, 1)),
        Static(RotY(N, 0, np.pi / 2)),
        Static(RotX(N, 1, np.pi / 2)),
        Static(Reverse(N, 0))
    ]

    q = QuantumCircuit(N, parts)

    return q


def create_qaoa_circuit(N, p):
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

    return QuantumCircuit(N, parts)
