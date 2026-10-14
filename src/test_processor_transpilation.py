
import json
from pathlib import Path

from qiskit import QuantumCircuit, transpile
from processors import load_phase1_processors


def build_test_circuit():
    circuit = QuantumCircuit(5)

    # Create interactions across several pairs of qubits.
    circuit.h(range(5))
    circuit.cx(0, 4)
    circuit.cx(1, 3)
    circuit.cx(0, 2)
    circuit.cx(4, 1)
    circuit.cx(2, 3)
    circuit.measure_all()

    return circuit


def main():
    processors = load_phase1_processors()
    circuit = build_test_circuit()
    results = {}

    for label, config in processors.items():
        settings = config["transpilation"]

        compiled = transpile(
            circuit,
            basis_gates=config["basis_gates"],
            coupling_map=config["coupling_map"],
            optimization_level=settings["optimization_level"],
            seed_transpiler=settings["seed_transpiler"],
        )

        gate_counts = dict(compiled.count_ops())

        results[label] = {
            "physical_qubits_available": config.get(
                "num_qubits", config.get("qubit_count")
            ),
            "transpiled_circuit_qubits": compiled.num_qubits,
            "circuit_depth": compiled.depth(),
            "gate_counts": gate_counts,
            "swap_count": gate_counts.get("swap", 0),
            "optimization_level": settings["optimization_level"],
            "seed_transpiler": settings["seed_transpiler"],
        }

        print(f"\nProcessor {label}")
        print("Circuit depth:", compiled.depth())
        print("Gate counts:", gate_counts)
        print("SWAP count:", gate_counts.get("swap", 0))

    output_path = Path("results/tables/connectivity_test.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nSaved results to {output_path}")


if __name__ == "__main__":
    main()
