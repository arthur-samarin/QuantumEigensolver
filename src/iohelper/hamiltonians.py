from qutip import Qobj
from iohelper.qio import qu_load
from npq import N_from_qobj, expected_value, qobj_to_np, classical_state
import numpy as np


class Hamiltonian:
    def __init__(self, matrix: Qobj):
        matrix.isherm = True
        self.H = matrix
        self.N = N_from_qobj(matrix)
        self.npH = qobj_to_np(self.H)
        self.min_eigenvalue = matrix.eigenenergies()[0]
        self.classical_psi0 = min(range(2**self.N), key=lambda i: expected_value(self.npH, classical_state(self.N, i)))
        self.classical_psi0_bitstring = ('{:0' + str(self.N) + 'b}').format(self.classical_psi0)

    @staticmethod
    def from_file(name):
        return Hamiltonian(qu_load(name))


q2 = Hamiltonian.from_file('H_H2_N=2')
q4 = Hamiltonian.from_file('H_LiH_N=4')
q8 = Hamiltonian.from_file('H_BeH2_N=8')
q10 = Hamiltonian.from_file('H_BeH2_N=10')


def h2(r):
    return Hamiltonian.from_file('h2/H_H2_N=4_R={}'.format(r))