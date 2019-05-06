from circuit import QCircuit, GateTypes, GateInstance
from iohelper import hamiltonians
import random


def uent(N):
    gates = []
    for i in range(1, N, 2):
        p = [i - 1, i]
        random.shuffle(p)
        gates.append(GateInstance(GateTypes.cnot, p))
    for i in range(2, N, 2):
        p = [i - 1, i]
        random.shuffle(p)
        gates.append(GateInstance(GateTypes.cnot, p))
    return gates


def rots(N, full=True):
    gates = []
    for i in range(0, N):
        if full:
            gates.append(GateInstance(GateTypes.rz, [i]))
        gates.append(GateInstance(GateTypes.rx, [i]))
        gates.append(GateInstance(GateTypes.rz, [i]))
    return gates


def kandala_circuit(N, classical_psi0, d):
    gates = []
    gates.extend(rots(N, full=False))
    for i in range(d):
        gates.extend(uent(N))
        gates.extend(rots(N))
    circ = QCircuit(N, classical_psi0, gates)
    return circ

