from quantum_circuit import Block, QuantumCircuit
from qutip import rx
import numpy as np
import scipy as sc

block = Block(2, 0, 1)
circ = QuantumCircuit(2, 0, [block])
identity = rx(0, N=2, target=0)


def f_to_min(parameters):
    circ.load_parameters(parameters)
    op = circ.as_operator() - identity
    v = np.sum(np.abs((op.full())))
    return v

parameters = np.zeros(circ.num_parameters)
res = sc.optimize.differential_evolution(f_to_min, [(0.0, 2*np.pi) for _ in range(8)])

print(res)