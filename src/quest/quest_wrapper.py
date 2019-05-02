import pyquest_cffi.utils
import pyquest_cffi.cheat
import pyquest_cffi.ops
import numpy as np
import npq


createQuestEnv = pyquest_cffi.utils.createQuestEnv()
createQureg = pyquest_cffi.utils.createQureg()
destroyQureg = pyquest_cffi.utils.destroyQureg()
initZeroState = pyquest_cffi.cheat.initZeroState()
pauliX = pyquest_cffi.ops.pauliX()
rotateX = pyquest_cffi.ops.rotateX()
rotateY = pyquest_cffi.ops.rotateY()
rotateZ = pyquest_cffi.ops.phaseShift()
controlledNot = pyquest_cffi.ops.controlledNot()
getAmp = pyquest_cffi.cheat.getAmp()

quest_env = createQuestEnv()


class Qureg:
    def __init__(self, n: int):
        self.n = n
        self._reg = createQureg(n, quest_env)

    def __del__(self):
        destroyQureg(self._reg, quest_env)
        self._reg = None

    def initialize_classical(self, classical_state: int):
        initZeroState(self._reg)
        for i in range(0, self.n):
            if (classical_state >> i) & 1 != 0:
                QuestOps.x(self, self.n - i - 1)

    def get_statevec(self) -> np.ndarray:
        statevec = np.zeros(2**self.n, dtype=np.complex)
        for i in range(2**self.n):
            statevec[i] = getAmp(self._reg, i)
        return statevec


class QuestOps:
    @staticmethod
    def x(qureg: Qureg, qubit: int):
        pauliX(qureg._reg, qubit)

    @staticmethod
    def rx(qureg: Qureg, qubit: int, angle: float):
        rotateX(qureg._reg, qubit, np.mod(angle, 4*np.pi))

    @staticmethod
    def ry(qureg: Qureg, qubit: int, angle: float):
        rotateY(qureg._reg, qubit, np.mod(angle, 4*np.pi))

    @staticmethod
    def rz(qureg: Qureg, qubit: int, angle: float):
        rotateZ(qureg._reg, qubit, np.mod(angle, 2*np.pi))

    @staticmethod
    def cnot(qureg: Qureg, control: int, target: int):
        controlledNot(qureg._reg, control, target)
