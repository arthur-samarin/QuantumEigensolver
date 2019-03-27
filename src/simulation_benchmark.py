from qio import qu_load
from qutip import tensor, basis
from circuits import create_qaoa_circuit
import npq
import qiskit as qk
import timeit

N = 8
H = qu_load('H_BeH2_N=8')
H.isherm = True
psi0 = tensor(basis(2, 1), basis(2, 1), basis(2, 0), basis(2, 0), basis(2, 0), basis(2, 0), basis(2, 0),
              basis(2, 0)).unit()

npH = H.full()
npPsi0 = psi0.full().flatten()
classicPsi0 = npq.to_classic_state(npPsi0)

qaoa = create_qaoa_circuit(N, classicPsi0, 5)
print(qaoa.as_qiskit_circuit().draw(line_length=240))


def compute_via_qutip():
    qaoa.as_operator() * psi0

def create_qiskit_circuit():
    qaoa.as_qiskit_circuit()

def run_statevector_simulation():
    qaoa.run_qiskit_simulation()

def run_qasm_simulation():
    qaoa.run_qiskit_simulation(backend_type='qasm_simulator')


circ = qaoa.as_qiskit_circuit()
backend_sim = qk.BasicAer.get_backend('qasm_simulator')

def run_fast_qasm_simulation():
    result = qk.execute(circ, backend_sim).result()


print(timeit.timeit(compute_via_qutip, number=10))
print(timeit.timeit(create_qiskit_circuit, number=10))
print(timeit.timeit(run_statevector_simulation, number=10))
print(timeit.timeit(run_qasm_simulation, number=10))
print(timeit.timeit(run_fast_qasm_simulation, number=10))