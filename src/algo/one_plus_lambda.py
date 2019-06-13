import time
from multiprocessing import Pool
from typing import Optional, List, Callable

from algo.vqe import Vqe, VqeResult
from circuit import QCircuit
from mutations import Mutation


class MutationReport:
    def __init__(self, circ: QCircuit, value: float, num_circ_evaluations: int, vqe_time: float):
        self.circ = circ
        self.value = value
        self.num_circ_evaluations = num_circ_evaluations
        self.vqe_time = vqe_time
        self.circuit_size = circ.size


class IterationReport:
    def __init__(self, index: int, better: bool, mutations: List[MutationReport], time: float):
        self.index = index
        self.better = better
        self.mutations = mutations
        self.time = time


class EvolutionReport:
    def __init__(self, iterations: List[IterationReport], best_iteration_index: int, interrupted: bool = False):
        self.iterations = iterations
        self.best_iteration_index = best_iteration_index
        self.interrupted = interrupted

    @property
    def best_circuit(self):
        return self.iterations[self.best_iteration_index].mutations[0].circ

    @property
    def best_circuit_value(self):
        return self.iterations[self.best_iteration_index].mutations[0].value

    @property
    def all_mutations(self):
        return [m for i in self.iterations for m in i.mutations]


class OnePlusLambda:
    def __init__(self, target: float, vqe: Vqe, mutation: Mutation, initial: QCircuit, target_eps=0.0016, alambda: int = 8, max_ev: int = None):
        self.initial = initial
        self.vqe = vqe
        self.mutation = mutation
        self.target = target
        self.target_eps = target_eps
        self.alambda = alambda
        self.max_ev = max_ev
        self.num_iterations = 0
        self.best_result: Optional[MutationReport] = None

    def run(self, iteration_end_callback: Callable[[IterationReport], None] = None) -> EvolutionReport:
        iterations = []
        best_iteration_index = 0
        interrupted = False
        num_evaluations_performed = 0
        iteration_start_time = time.time()

        with Pool(initializer=OnePlusLambda._initialize_subprocess, initargs=(self.vqe,)) as p:
            self.best_result = p.apply(self._evaluate_mutation, [self.initial])
            print('Initial value: {}'.format(self.best_result.value))
            iterations.append(IterationReport(0, True, [self.best_result], time.time() - iteration_start_time))

            num_iterations_without_progress = 0
            self.num_iterations = 0
            try:
                while self.best_result.value > self.target + self.target_eps \
                        and (self.max_ev is None or num_evaluations_performed < self.max_ev):
                    iteration_start_time = time.time()

                    # Mutate
                    mutated_circuits = []
                    for _ in range(self.alambda):
                        circuit_clone = self.best_result.circ.clone()
                        self.mutation.apply(circuit_clone)
                        if num_iterations_without_progress >= 4:
                            # Try to do more complex mutations
                            for j in range(0, int(num_iterations_without_progress**0.5)):
                            # for j in range(0, 1):
                                self.mutation.apply(circuit_clone)
                        mutated_circuits.append(circuit_clone)

                    # Evaluate
                    mutation_reports = list(p.imap_unordered(OnePlusLambda._evaluate_mutation, mutated_circuits))
                    mutation_reports.sort(key=lambda r: r.value)
                    new_result: MutationReport = mutation_reports[0]

                    # Increment iteration number and number of evaluations
                    self.num_iterations += 1
                    for m in mutation_reports:
                        num_evaluations_performed += m.num_circ_evaluations

                    # Check if better
                    is_better = new_result.value < self.best_result.value
                    iteration_report = IterationReport(self.num_iterations, is_better, mutation_reports,
                                                       time.time() - iteration_start_time)
                    iterations.append(iteration_report)

                    # Choose best
                    if is_better:
                        self.best_result = new_result
                        best_iteration_index = self.num_iterations

                        num_iterations_without_progress = 0
                    else:
                        num_iterations_without_progress += 1

                    if iteration_end_callback is not None:
                        iteration_end_callback(iteration_report)
            except KeyboardInterrupt:
                interrupted = True

        return EvolutionReport(iterations, best_iteration_index, interrupted=interrupted)

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
    def _evaluate_mutation(circuit: QCircuit) -> MutationReport:
        import time
        start_time = time.time()
        vqe_result = OnePlusLambda._vqe.optimize(circuit)
        circuit.set_parameters(vqe_result.opt_parameters)
        return MutationReport(circuit, vqe_result.opt_value, vqe_result.num_evaluations, time.time() - start_time)
