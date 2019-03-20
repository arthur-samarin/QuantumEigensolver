from qio import qu_load
from qutip import tensor, basis
from circuits import create_qaoa_circuit
import timeit

N = 8
H = qu_load('H_BeH2_N=8')
H.isherm = True
psi0 = tensor(basis(2, 1), basis(2, 1), basis(2, 0), basis(2, 0), basis(2, 0), basis(2, 0), basis(2, 0),
              basis(2, 0)).unit()

npH = H.full()
npPsi0 = psi0.full().flatten()

qaoa = create_qaoa_circuit(N, 5)
print(qaoa.as_qiskit_circuit(npPsi0).draw(line_length=240))


def compute_via_qutip():
    qaoa.as_operator() * psi0

def compute_via_qiskit():
    qaoa.apply_to_state(npPsi0)

print(timeit.timeit(compute_via_qutip, number=100))
print(timeit.timeit(compute_via_qiskit, number=100))