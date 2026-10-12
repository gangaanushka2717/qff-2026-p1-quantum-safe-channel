
from src.processors import load_processor
import json
from pathlib import Path


def compare_processors(a, b):
    results = []

    for processor in [a, b]:
        qubits = processor["qubit_count"]
        edges = processor["coupling_map"]

        results.append({
            "name": processor["name"],
            "qubits": qubits,
            "connections": len(edges),
            "connection_density": round(
                2 * len(edges) / (qubits * (qubits - 1)), 4
            ),
            "average_degree": round(
                2 * len(edges) / qubits, 3
            ),
            "basis_gates_available": processor["basis_gates"] is not None,
            "noise_model_available": processor["noise_model"] is not None,
            "configuration_status": processor["configuration_status"],
        })

    return results


processor_a = load_processor("processors/processor_A.json")
processor_b = load_processor("processors/processor_B.json")

comparison = compare_processors(processor_a, processor_b)

output = Path("results/tables")
output.mkdir(parents=True, exist_ok=True)
(output / "processor_topology_comparison.json").write_text(
    json.dumps(comparison, indent=2),
    encoding="utf-8",
)

print(json.dumps(comparison, indent=2))
print("\nSaved results/tables/processor_topology_comparison.json")
