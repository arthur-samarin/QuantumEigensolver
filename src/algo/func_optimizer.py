import numpy as np
import cma
import scipy as sc


class OptimizationResult:
    def __init__(self, x_opt: np.ndarray, f_opt: float, optimizer_data=None):
        self.x_opt = x_opt
        self.f_opt = f_opt
        self.optimizer_data = optimizer_data


class Optimizer:
    def optimize(self, f, x0, bounds):
        raise NotImplemented()


class BfgsOptimizer(Optimizer):
    def optimize(self, f, x0, bounds):
        [xopt, fopt, gopt, Bopt, func_calls, grad_calls, warnflg] = sc.optimize.fmin_bfgs(f, x0,
                                                                                          full_output=True,
                                                                                          disp=False)
        return OptimizationResult(xopt, fopt)


class CmaesOptimizer(Optimizer):
    def __init__(self, precision: float = 1e-11, iterations=None):
        self.precision = precision
        self.iterations = iterations

    def optimize(self, f, x0, bounds):
        lower = [b[0] for b in bounds]
        upper = [b[1] for b in bounds]

        es = cma.CMAEvolutionStrategy(x0, 0.5, {
            'verbose': 0, 'verb_log': 0, 'verb_plot': 0, 'verb_disp': 0,
            'tolfun': self.precision,
            'bounds': (lower, upper)
        })

        es.optimize(f, iterations=self.iterations)

        return OptimizationResult(es.result.xbest, es.result.fbest, {
            'num_iterations': es.result.iterations
        })

    @staticmethod
    def _noop(*args, **kwargs):
        pass
