import qiskit as qk

qr = qk.QuantumRegister(2)
c = qk.QuantumCircuit(qr)
c.cx(qr[0], qr[1])
c.swap(qr[0], qr[1])
print(c.draw(line_length=240))