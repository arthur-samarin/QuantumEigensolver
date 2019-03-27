import numpy as np
import scipy as sc
from qutip import *

import mutations
import npq
from circuits import create_qaoa_circuit
from qio import qu_load
from quantum_circuit import QuantumCircuit

# N = 2
# H = qu_load('H2')
# H.isherm = True
# psi0 = tensor(basis(2,0),basis(2,1)).unit()
N = 8
H = qu_load('H_BeH2_N=8')
H.isherm = True
psi0 = tensor(basis(2, 1), basis(2, 1), basis(2, 0), basis(2, 0), basis(2, 0), basis(2, 0), basis(2, 0),
              basis(2, 0)).unit()
# N = 10
# H = qu_load('H_BeH2_N=10')
# H.isherm = True
# psi0 = tensor(basis(2,1),basis(2,1),basis(2,1),basis(2,1),basis(2,0),basis(2,0),basis(2,0),basis(2,0),basis(2,0),basis(2,0)).unit()
psi0_classic = npq.to_classic_state(npq.qobj_to_np(psi0))

npH = npq.qobj_to_np(H)
npPsi0 = npq.qobj_to_np(psi0)
classicPsi0 = npq.to_classic_state(npPsi0)

vals, vecs = H.eigenstates()
min_eigenvalue = vals[0]
eigenvalue_eps = 0.0016
print('Minimal eigenvalue is  {}'.format(vals.min()))

num_evaluations = 0


def score_circuit(schema: QuantumCircuit):
    def E_to_min(params):
        global num_evaluations
        num_evaluations += 1

        schema.load_parameters(params)

        # op = schema.as_operator()
        # phi = op * psi0
        # e = expect(H, phi)

        phi_q = schema.run_qiskit_simulation()
        e2 = npq.expected_value(npH, phi_q)

        # assert np.isclose(e, e2)

        return e2

    if schema.num_parameters == 0:
        # Don't run optimizations for schemas without parameters because it crashes some methods
        return E_to_min(np.zeros(0))

    parameters = np.random.uniform(0.0, 2 * np.pi, schema.num_parameters)
    # parameters = sc.optimize.minimize(E_to_min, parameters, method='nelder-mead', options={'xtol': 1e-4, 'disp': False}).x
    # return E_to_min(parameters)
    # res = sc.optimize.basinhopping(E_to_min, parameters, niter=5, disp=False)
    # return res.fun

    # res = sc.optimize.differential_evolution(E_to_min,
    #           [(0.0, 2*np.pi) for i in range(0, len(parameters))],
    #           disp = False)
    # return res.fun
    [xopt, fopt, gopt, Bopt, func_calls, grad_calls, warnflg] = sc.optimize.fmin_bfgs(E_to_min, parameters, full_output=True, disp=False)
    return fopt


# Estimate QAOA schema
# print('Using VQE on QAOA circuit, that may take a while.')
# qaoa_result = score_schema(create_qaoa_circuit(N, classicPsi0, 5))
# print('QAOA result is {}'.format(qaoa_result))

# Initialize circuit with something random
circuit = QuantumCircuit(N, classicPsi0)
for i in range(0, 10):
    mutations.random_mutation(circuit)

best_score = score_circuit(circuit)
print('Initial value: {}'.format(best_score))
num_iterations = 1
num_iterations_without_progress = 0

try:
    while best_score > min_eigenvalue + eigenvalue_eps:
        num_iterations += 1
        # Mutate
        circuit_clone = circuit.clone()
        mutations.random_mutation(circuit_clone)
        if num_iterations_without_progress >= 10:
            # Try to do more complex mutations
            for j in range(0, num_iterations_without_progress // 2):
                mutations.random_mutation(circuit_clone)

        # Evaluate
        new_score = score_circuit(circuit_clone)
        if new_score < best_score:
            print('New value: {} at iteration {}'.format(new_score, num_iterations))
            best_score = new_score
            circuit = circuit_clone

            num_iterations_without_progress = 0
        else:
            num_iterations_without_progress += 1
except KeyboardInterrupt:
    print("INTERRUPTED")

print('Best value is: ' + str(best_score))
print('Number of iterations is {}'.format(num_iterations))
print('Number of circuit evaluations is {}'.format(num_evaluations))
print(circuit.as_qiskit_circuit().draw(line_length=240))
