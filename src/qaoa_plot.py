import circuits
import npq
import numpy as np
import scipy as sc
from qio import qu_load
from qutip import *
from quantum_circuit import QuantumCircuit


N = 8
H = qu_load('H_BeH2_N=8')
H.isherm = True
psi0 = tensor(basis(2, 1), basis(2, 1), basis(2, 0), basis(2, 0), basis(2, 0), basis(2, 0), basis(2, 0),
              basis(2, 0)).unit()
npH = npq.qobj_to_np(H)
classicPsi = npq.to_classic_state(npq.qobj_to_np(psi0))


def score_circuit(schema: QuantumCircuit):
    def E_to_min(params):
        schema.load_parameters(params)

        op = schema.as_operator()
        phi = op * psi0
        e = expect(H, phi)

        # phi_q = schema.run_qiskit_simulation()
        # e = npq.expected_value(npH, phi_q)

        return e

    if schema.num_parameters == 0:
        # Don't run optimizations for schemas without parameters because it crashes some methods
        return E_to_min(np.zeros(0))

    parameters = np.random.uniform(0.0, 2 * np.pi, schema.num_parameters)
    [xopt, fopt, gopt, Bopt, func_calls, grad_calls, warnflg] = sc.optimize.fmin_bfgs(E_to_min, parameters, full_output=True, disp=False)
    return fopt


for i in range(0, 6):
    for j in range(0, 4):
        circuit = circuits.create_qaoa_circuit(N, classicPsi, i)
        print(i, score_circuit(circuit))