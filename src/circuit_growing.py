from qutip import *
from qio import qu_load
import numpy as np
import scipy as sc
from quantum_circuit import QuantumCircuit, CNot, RotX, RotY, RotZ, Reverse, Static
from circuits import create_qaoa_circuit
import mutations

N = 2
H = qu_load('H2')
H.isherm = True
psi0 = tensor(basis(2,0),basis(2,1)).unit()
# N = 8
# H = qu_load('H_BeH2_N=8')
# H.isherm = True
# psi0 = tensor(basis(2, 1), basis(2, 1), basis(2, 0), basis(2, 0), basis(2, 0), basis(2, 0), basis(2, 0),
#               basis(2, 0)).unit()
# N = 10
# H = qu_load('H_BeH2_N=10')
# H.isherm = True
# psi0 = tensor(basis(2,1),basis(2,1),basis(2,1),basis(2,1),basis(2,0),basis(2,0),basis(2,0),basis(2,0),basis(2,0),basis(2,0)).unit()

vals, vecs = H.eigenstates()
min_eigenvalue = vals[0]
eigenvalue_eps = 0.0016
print('Minimal eigenvalue is  {}'.format(vals.min()))


def score_schema(schema: QuantumCircuit):
    def E_to_min(params):
        schema.load_parameters(params)
        op = schema.as_operator()
        phi = op * psi0
        e = expect(H, phi)
        return e

    if schema.num_parameters == 0:
        # Don't run optimizations for schemas without parameters because it crashes some methods
        return E_to_min(np.zeros(0))

    parameters = np.zeros((schema.num_parameters,), dtype=np.double)
    schema.store_parameters(parameters)

    res = sc.optimize.basinhopping(E_to_min, parameters, disp=False)
    return res.fun
    # res = sc.optimize.differential_evolution(E_to_min,
    #           [(0.0, 2*np.pi) for i in range(0, len(parameters))],
    #           disp = False)
    # return res.fun
    # [xopt, fopt, gopt, Bopt, func_calls, grad_calls, warnflg] = sc.optimize.fmin_bfgs(E_to_min, parameters, full_output=True, disp=False)
    # return fopt


# Estimate QAOA schema
print('Using VQE on QAOA circuit, that may take a while.')
qaoa_result = score_schema(create_qaoa_circuit(N, 5))
print('QAOA result is {}'.format(qaoa_result))

# Initialize circuit with something random
schema = QuantumCircuit(N)
for i in range(0, 10):
    mutations.random_mutation(schema)

#
best_score = score_schema(schema)
print('Initial value: {}'.format(best_score))
num_iterations = 1
num_iterations_without_progress = 0
while best_score > min_eigenvalue + eigenvalue_eps:
    num_iterations += 1

    # Mutate
    schema_clone = schema.clone()
    mutations.random_mutation(schema_clone)
    if num_iterations_without_progress >= 50:
        # Try to do more complex mutations
        for j in range(0, 5):
            mutations.random_mutation(schema_clone)

    # Evaluate
    new_score = score_schema(schema_clone)
    if new_score < best_score:
        print('New value: {} at iteration {}'.format(new_score, num_iterations))
        best_score = new_score
        schema = schema_clone

        num_iterations_without_progress = 0
    else:
        num_iterations_without_progress += 1

print('Best value is: ' + str(best_score))
print('Number of iterations is {}'.format(num_iterations))
