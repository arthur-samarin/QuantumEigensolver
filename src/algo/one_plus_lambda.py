from quantum_circuit import QuantumCircuit
from multiprocessing import Pool


class OnePlusLambda:
    def __init__(self, target: float, evaluate, mutate, initial: QuantumCircuit, target_eps=0.0016, alambda: int = 8):
        self.initial = initial
        self.evaluate = evaluate
        self.mutate = mutate
        self.target = target
        self.target_eps = target_eps
        self.alambda = 8
        self.num_iterations = 0

        self.best_score = None
        self.best_circuit = None

    def run(self):
        with Pool(initializer=OnePlusLambda._initialize_subprocess, initargs=(self.evaluate, )) as p:
            self.best_circuit = self.initial
            self.best_score = self.evaluate(self.initial)
            print('Initial value: {}'.format(self.best_score))

            num_iterations_without_progress = 0
            self.num_iterations = 0
            try:
                while self.best_score > self.target + self.target_eps:
                    # Mutate
                    mutated_circuits = []
                    for _ in range(self.alambda):
                        circuit_clone = self.best_circuit.clone()
                        self.mutate(circuit_clone)
                        if num_iterations_without_progress >= 10:
                            # Try to do more complex mutations
                            for j in range(0, num_iterations_without_progress // 2):
                                self.mutate(circuit_clone)
                        mutated_circuits.append(circuit_clone)

                    # Evaluate
                    evaluation_results = list(p.imap_unordered(OnePlusLambda._evaluate_in_subprocess, mutated_circuits))
                    new_circuit, new_score = min(evaluation_results, key=lambda pair: pair[1])

                    # Increment iteration number
                    self.num_iterations += 1

                    # Choose best
                    if new_score < self.best_score:
                        print('New value: {} at iteration {}'.format(new_score, self.num_iterations))
                        self.best_score = new_score
                        self.best_circuit = new_circuit

                        num_iterations_without_progress = 0
                    else:
                        num_iterations_without_progress += 1

            except KeyboardInterrupt:
                print("INTERRUPTED")

    """Local to subprocess"""
    _evaluate = None

    @staticmethod
    def _initialize_subprocess(evfunc):
        try:
            import signal
            signal.signal(signal.SIGINT, signal.SIG_IGN)
        except:
            # Probably doesn't work on Windows, ignore that
            pass

        OnePlusLambda._evaluate = evfunc

    @staticmethod
    def _evaluate_in_subprocess(circuit: QuantumCircuit):
        result = OnePlusLambda._evaluate(circuit)
        return circuit, result
