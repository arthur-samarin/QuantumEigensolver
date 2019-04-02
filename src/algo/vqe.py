from qutip import Qobj, expect
from npq import classical_state, N_from_qobj, np_to_ket
from quantum_circuit import QuantumCircuit
import numpy as np
import scipy as sc


class Vqe:
    def __init__(self, hamiltonian: Qobj):
        self.N = N_from_qobj(hamiltonian)
        self.H = hamiltonian
        self.num_circuit_evaluations = 0
        self.num_optimizations = 0

    def optimize(self, circuit: QuantumCircuit):
        def e_to_min(params):
            self.num_circuit_evaluations += 1
            circuit.load_parameters(params)
            op = circuit.as_operator()
            phi = op * np_to_ket(classical_state(self.N, circuit.initial_classic_state))
            e = expect(self.H, phi)
            return e

        self.num_optimizations += 1
        if circuit.num_parameters == 0:
            # Don't run optimizations for schemas without parameters because it crashes some methods
            return e_to_min(np.zeros(0))

        parameters = np.random.uniform(0.0, 2 * np.pi, circuit.num_parameters)
        [xopt, fopt, gopt, Bopt, func_calls, grad_calls, warnflg] = sc.optimize.fmin_bfgs(e_to_min, parameters,
                                                                                          full_output=True,
                                                                                          disp=False)

        circuit.load_parameters(xopt)
        return fopt
