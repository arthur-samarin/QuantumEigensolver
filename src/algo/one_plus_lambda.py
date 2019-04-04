from multiprocessing import Pool
from typing import Optional

from algo.vqe import Vqe, VqeResult
from circuit import QCircuit


class OnePlusLambda:
    def __init__(self, target: float, vqe: Vqe, mutate, initial: QCircuit, target_eps=0.0016, alambda: int = 8):
        self.initial = initial
        self.vqe = vqe
        self.mutate = mutate
        self.target = target
        self.target_eps = target_eps
        self.alambda = alambda
        self.num_iterations = 0

        self.best_result: Optional[VqeResult] = None

    def run(self):
        with Pool(initializer=OnePlusLambda._initialize_subprocess, initargs=(self.vqe, )) as p:
            self.best_result = self.vqe.optimize(self.initial)
            print('Initial value: {}'.format(self.best_result.opt_value))

            num_iterations_without_progress = 0
            self.num_iterations = 0
            try:
                while self.best_result.opt_value > self.target + self.target_eps:
                    # Display iteration number
                    print('Iteration #{}...'.format(self.num_iterations + 1))

                    # Mutate
                    mutated_circuits = []
                    for _ in range(self.alambda):
                        circuit_clone = self.best_result.circ.clone()
                        self.mutate(circuit_clone)
                        if num_iterations_without_progress >= 10:
                            # Try to do more complex mutations
                            for j in range(0, num_iterations_without_progress // 2):
                                self.mutate(circuit_clone)
                        mutated_circuits.append(circuit_clone)

                    # Evaluate
                    evaluation_results = list(p.imap_unordered(OnePlusLambda._evaluate_in_subprocess, mutated_circuits))
                    new_result: VqeResult = min(evaluation_results, key=lambda r: r.opt_value)

                    # Increment iteration number
                    self.num_iterations += 1

                    # Choose best
                    if new_result.opt_value < self.best_result.opt_value:
                        print('New value: {} at iteration {}'.format(new_result.opt_value, self.num_iterations))
                        self.best_result = new_result
                        self.best_result.circ.set_parameters(new_result.opt_parameters)

                        num_iterations_without_progress = 0
                    else:
                        num_iterations_without_progress += 1

            except KeyboardInterrupt:
                print("INTERRUPTED")

    """Local to subprocess"""
    _vqe = None

    @staticmethod
    def _initialize_subprocess(vqe):
        try:
            import signal
            signal.signal(signal.SIGINT, signal.SIG_IGN)
        except:
            # Probably doesn't work on Windows, ignore that
            pass

        OnePlusLambda._vqe = vqe

    @staticmethod
    def _evaluate_in_subprocess(circuit: QCircuit):
        return OnePlusLambda._vqe.optimize(circuit)
