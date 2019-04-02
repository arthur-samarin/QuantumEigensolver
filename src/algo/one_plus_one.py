from quantum_circuit import QuantumCircuit


class OnePlusOne:
    def __init__(self, target: float, evaluate, mutate, initial: QuantumCircuit, target_eps=0.0016):
        self.initial = initial
        self.evaluate = evaluate
        self.mutate = mutate
        self.target = target
        self.target_eps = target_eps

        self.best_score = None
        self.best_circuit = None

    def run(self):
        self.best_circuit = self.initial
        self.best_score = self.evaluate(self.initial)
        print('Initial value: {}'.format(self.best_score))

        num_iterations_without_progress = 0
        num_iterations = 0
        try:
            while self.best_score > self.target + self.target_eps:
                num_iterations += 1

                # Mutate
                circuit_clone = self.best_circuit.clone()
                self.mutate(circuit_clone)
                if num_iterations_without_progress >= 10:
                    # Try to do more complex mutations
                    for j in range(0, num_iterations_without_progress // 2):
                        self.mutate(circuit_clone)

                # Evaluate
                new_score = self.evaluate(circuit_clone)
                if new_score < self.best_score:
                    print('New value: {} at iteration {}'.format(new_score, num_iterations))
                    self.best_score = new_score
                    self.best_circuit = circuit_clone

                    num_iterations_without_progress = 0
                else:
                    num_iterations_without_progress += 1

        except KeyboardInterrupt:
            print("INTERRUPTED")
