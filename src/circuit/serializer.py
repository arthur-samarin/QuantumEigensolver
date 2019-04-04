from circuit import QCircuit, GateTypes, GateInstance
import numpy as np
import re


class QCircuitSerializer:
    _re_qubits = re.compile(r'^qubits\s+(\d+)$')
    _re_prepare = re.compile(r'^prepare\s+([01]+)$')
    _re_gate = re.compile(r'^gate\s+([\w-]+)\s*\[([^\]]*)\]\s*\[([^\]]*)\]$')

    @staticmethod
    def from_str(serialized: str) -> QCircuit:
        num_qubits = None
        initial_state = None
        gates = []

        for line in serialized.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            m_qubits = QCircuitSerializer._re_qubits.match(line)
            m_prepare = QCircuitSerializer._re_prepare.match(line)
            m_gate = QCircuitSerializer._re_gate.match(line)

            if m_qubits:
                num_qubits = int(m_qubits.group(1))
            elif m_prepare:
                initial_state = int(m_prepare.group(1), 2)
            elif m_gate:
                typ = GateTypes.by_name(m_gate.group(1))
                qubits_list = [int(p.strip()) for p in m_gate.group(2).split(',')]
                params_list = [float(p.strip()) for p in m_gate.group(3).split(',')]
                gates.append(GateInstance(typ, qubits_list, params_list))
            else:
                raise ValueError('Bad line: {}'.format(line))

        if initial_state is None:
            raise ValueError('No prepare statement')
        if num_qubits is None:
            raise ValueError('No qubits statement')

        return QCircuit(num_qubits, initial_state, gates)

    @staticmethod
    def to_str(circ: QCircuit) -> str:
        num_qubits = circ.num_qubits
        initial_state_bitstring = ('{:0' + str(num_qubits) + 'b}').format(circ.initial_classical_state)

        result = 'qubits {}\n'.format(num_qubits)
        result += 'prepare {}\n'.format(initial_state_bitstring)
        for gate in circ.gates:
            typ = gate.typ
            result += 'gate '
            result += typ.name
            result += ' [' + ', '.join(map(str, gate.qubits)) + ']'
            result += ' [' + ', '.join(map(str, gate.params)) + ']'
            result += '\n'

        return result

