
import json
from pathlib import Path

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError

from processors import load_phase1_processors


def build_noise_model(config):
    noise = config["noise_model"]
    model = NoiseModel()

    one_qubit_error = depolarizing_error(
        noise["one_qubit_depolarizing_probability"], 1
    )
    two_qubit_error = depolarizing_error(
        noise["two_qubit_cx_depolarizing_probability"], 2
    )

    model.add_all_qubit_quantum_error(
        one_qubit_error, ["rz", "sx", "x"]
    )
    model.add_all_qubit_quantum_error(
        two_qubit_error, ["cx"]
    )

    readout_probability = noise["readout_error_probability"]
    readout_error = ReadoutError([
        [1 - readout_probability, readout_probability],
        [readout_probability, 1 - readout_probability],
    ])

    model.add_all_qubit_readout_error(readout_error)
    return model


def main():
    processors = load_phase1_processors()
    all_results = {}

    # Same circuit for both processor configurations.
    circuit = QuantumCircuit(5)
    circuit.h(range(5))
    circuit.cx(0, 4)
    circuit.cx(1, 3)
    circuit.cx(0, 2)
    circuit.cx(4, 1)
    circuit.cx(2, 3)
    circuit.measure_all()

    for label, config in processors.items():
        settings = config["transpilation"]
        noise_model = build_noise_model(config)
        simulator = AerSimulator(noise_model=noise_model)

        compiled = transpile(
            circuit,
            basis_gates=config["basis_gates"],
            coupling_map=config["coupling_map"],
            optimization_level=settings["optimization_level"],
            seed_transpiler=settings["seed_transpiler"],
        )

        result = simulator.run(
            compiled,
            shots=settings["shots"],
            seed_simulator=settings["seed_transpiler"],
        ).result()

        counts = result.get_counts()
        gate_counts = dict(compiled.count_ops())

        all_results[label] = {
            "shots": settings["shots"],
            "counts": counts,
            "circuit_depth": compiled.depth(),
            "gate_counts": gate_counts,
            "swap_count": gate_counts.get("swap", 0),
            "noise_model": config["noise_model"],
            "optimization_level": settings["optimization_level"],
            "seed_transpiler": settings["seed_transpiler"],
            "seed_simulator": settings["seed_transpiler"],
        }

        print(f"\nProcessor {label}")
        print("Shots:", settings["shots"])
        print("Counts:", counts)
        print("Circuit depth:", compiled.depth())
        print("Gate counts:", gate_counts)
        print("SWAP count:", gate_counts.get("swap", 0))
        print("Noise model: applied")
        print("Readout error:", config["noise_model"][
            "readout_error_probability"
        ])

    # Save both processors' results after the loop.
    output_path = Path("results/tables/noisy_simulation.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(all_results, indent=2),
        encoding="utf-8",
    )

    print(f"\nSaved results to {output_path}")


if __name__ == "__main__":
    main()
