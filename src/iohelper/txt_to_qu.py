from typing import List, Tuple
import qutip
import re

from iohelper import qio


class MeasurementOp:
    def __init__(self, N: int, chains: List[Tuple[float, List[Tuple[str, int]]]] = None):
        self.chains = chains or []
        self.N = N

    def to_qobj(self) -> qutip.Qobj:
        H = qutip.qzero([[2] * self.N])
        for value, chain in self.chains:
            chain_op = qutip.rx(0, self.N, 0)

            for gate, target in chain:
                if gate == 'X':
                    chain_op = qutip.gate_expand_1toN(qutip.sigmax(), self.N, target) * chain_op
                elif gate == 'Y':
                    chain_op = qutip.gate_expand_1toN(qutip.sigmay(), self.N, target) * chain_op
                elif gate == 'Z':
                    chain_op = qutip.gate_expand_1toN(qutip.sigmaz(), self.N, target) * chain_op

            chain_op = chain_op * value
            H = H + chain_op
        return H

    @staticmethod
    def from_file(N: int, name: str):
        chain_re = re.compile("^([\\d.e+-]+)\\s*\\[(.*)\\]\\s*[+]?$")

        chains = []
        with open(name, 'rt') as f:
            for line in f:
                line = line.strip().replace(':', '')
                if not line:
                    continue
                m = chain_re.match(line)
                value = float(m.group(1))
                gate_chain = []
                for gate in m.group(2).split():
                    gate_chain.append((gate[0], int(gate[1:])))
                chains.append((value, gate_chain))
        return MeasurementOp(N, chains)


if __name__ == '__main__':
    N = 4
    name = 'H_LiH_N=4'
    op = MeasurementOp.from_file(N, 'input/{}.txt'.format(name))
    H = op.to_qobj()
    H2 = qio.qu_load(name)
    qio.qu_save(name, H)

    import numpy as np
    print(np.max(np.abs(H.full() - H2.full())))
