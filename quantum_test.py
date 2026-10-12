
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

# Create a simple 1-qubit quantum circuit
circuit = QuantumCircuit(1)
circuit.h(0)

# Simulate the circuit's quantum state
state = Statevector.from_instruction(circuit)

print("Quantum circuit:")
print(circuit.draw())
print("Statevector:", state)
