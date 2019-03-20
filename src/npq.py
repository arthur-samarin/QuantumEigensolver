"""
Quantum operations with numpy arrays.

For wavefunction vectors:
  Numpy array = one-dimensional array with values of ket-vector
"""

import numpy as np
from qutip import Qobj


def classic_states(N: int):
    for i in range(0, N):
        yield np.array([0] * i + [1.0] + [0] * (2 ** N - i - 1), dtype=np.complex)


def zero_state(N: int):
    return np.array([1.0] + [0] * (2 ** N - 1), dtype=np.complex)


# wavefunction'[i] = wavefunction[reverse(i)]
# where reverse() is reverse of binary form
def reverse_qubits_in_state(state):
    N = N_from_state_vector(state)
    return state[reverse_qubits_permutation(N)]


def reverse_qubits_permutation(N):
    permutation = np.zeros(2**N, dtype=np.int)
    for i in range(0, 2**N):
        k = i
        reverse = 0
        for j in range(0, N):
            reverse = reverse << 1
            reverse = reverse | (k & 1)
            k = k >> 1
        permutation[i] = reverse
    return permutation


def np_to_ket(arr: np.ndarray) -> Qobj:
    N = N_from_state_vector(arr)
    return Qobj(np.row_stack(arr), dims=[[2] * N, [1] * N])


def N_from_state_vector(arr):
    M, = arr.shape
    N = M.bit_length() - 1
    if 2 ** N != M:
        raise ValueError("Bad array size: {}, must me a power of 2.".format(M))
    return N


def qobj_to_np(obj: Qobj) -> np.ndarray:
    if obj.isket:
        return obj.full().flatten()
    elif obj.isbra:
        return obj.full().flatten().conj()
    elif obj.isoper:
        return obj.full()
    else:
        raise ValueError("Qobj is not ket or bra")


def expected_value(H, state) -> np.ndarray:
    z1 = np.matmul(state.conj(), H)
    ev = np.dot(z1, state)
    assert(np.isclose(np.imag(ev), 0))
    return np.real(ev)