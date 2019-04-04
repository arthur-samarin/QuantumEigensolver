import numpy as np
from qutip import Qobj, expect

from algo.func_optimizer import Optimizer, OptimizationResult
from circuit import QCircuit, QCircuitConversions
from npq import N_from_qobj


class VqeResult:
    def __init__(self, circ: QCircuit, opt_parameters: np.ndarray, opt_value: float):
        self.circ = circ
        self.opt_parameters = opt_parameters
        self.opt_value = opt_value


class Vqe:
    def __init__(self, optimizer: Optimizer, hamiltonian: Qobj):
        self.N = N_from_qobj(hamiltonian)
        self.H = hamiltonian
        self.optimizer = optimizer

    def optimize(self, circ: QCircuit):
        def e_to_min(params):
            circ.set_parameters(params)
            wavefunc = QCircuitConversions.to_qobj_wavefunction(circ)
            e = expect(self.H, wavefunc)
            return e

        if circ.num_parameters == 0:
            # Don't run optimizations for schemas without parameters because it crashes some methods
            p = np.zeros(0)
            return VqeResult(circ, p, e_to_min(p))

        parameters = np.random.uniform(0.0, np.pi, circ.num_parameters)

        result: OptimizationResult = self.optimizer.optimize(e_to_min, parameters, circ.parameters_bounds)
        return VqeResult(circ, result.x_opt, result.f_opt)
