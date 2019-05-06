import sys
import os
import numpy as np
from iohelper import hamiltonians

cvqe_path = os.path.abspath('cvqe/build')
sys.path.append(cvqe_path)

import cvqe
from cvqe import GateTypes, QCircuit, Vqe

c = QCircuit(2, 0)
print(c.num_parameters)
c.add_gate(GateTypes.block_a(), [0, 1])
vqe = Vqe(hamiltonians.q2.H.full())
result = vqe.optimize(c)
print(result.opt_value)
print(result.create_vector)
# print(result.opt_parameters)
