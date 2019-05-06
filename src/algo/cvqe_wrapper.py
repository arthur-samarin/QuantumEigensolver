from algo.vqe import VqeResult
from circuit import QCircuit
from . import vqe
import os
import sys
import numpy as np

cvqe_path = os.path.abspath('cvqe/build')
sys.path.append(cvqe_path)
import cvqe


class CVqe:
    def __init__(self, h, ftol=1e-6):
        self._vqe = cvqe.Vqe(h.full())
        self._vqe.ftol = ftol

    def optimize(self, circ: QCircuit) -> VqeResult:
        c_circ = cvqe.QCircuit(circ.num_qubits, circ.initial_classical_state)
        for gate in circ.gates:
            gate.typ.add_to_cvqe(gate, c_circ, cvqe.GateTypes)

        res = self._vqe.optimize(c_circ)
        circ.set_parameters(res.opt_parameters[:,0])
        return VqeResult(circ, res.opt_parameters[:,0], res.opt_value, res.num_evaluations, {'millis_taken': res.millis_taken})
