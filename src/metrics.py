from collections import Counter

def circuit_metrics(circuit):
    """Calculate structural metrics from a Qiskit QuantumCircuit."""
    counts = Counter(
        instruction.operation.name
        for instruction in circuit.data
    )

    return {
        "num_qubits": circuit.num_qubits,
        "depth": circuit.depth(),
        "gate_count": sum(counts.values()),
        "gate_counts": dict(counts),
        "cx_count": counts.get("cx", 0),
        "swap_count": counts.get("swap", 0),
        "fidelity": None,  # Requires a defined noise model or measured data.
    }


def summarize_results(results):
    """Summarize a non-empty list of result dictionaries."""
    if not results:
        raise ValueError("results must not be empty")

    successful_runs = sum(
        1 for result in results if result.get("success") is True
    )

    return {
        "num_runs": len(results),
        "success_rate": successful_runs / len(results),
    }
