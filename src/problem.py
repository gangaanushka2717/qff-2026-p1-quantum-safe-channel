import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def load_processor(path):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path

    with path.open("r", encoding="utf-8") as f:
        processor = json.load(f)

    # Support both the guide's schema and our existing JSON files.
    count = processor.get("num_qubits", processor.get("qubit_count"))
    edges = processor.get("coupling_map")

    if not isinstance(count, int) or count < 1:
        raise ValueError(f"Invalid qubit count in {path}")
    if not isinstance(edges, list):
        raise ValueError(f"Missing coupling_map in {path}")

    for edge in edges:
        if (not isinstance(edge, list) or len(edge) != 2
                or not all(isinstance(q, int) for q in edge)):
            raise ValueError(f"Invalid coupling edge: {edge}")
        if any(q < 0 or q >= count for q in edge):
            raise ValueError(f"Coupling edge outside processor: {edge}")

    return {
        **processor,
        "num_qubits": count,
        "coupling_map": edges,
    }

def load_phase1_processors():
    return {
        "A": load_processor("processors/processor_A.json"),
        "B": load_processor("processors/processor_B.json"),
    }

if __name__ == "__main__":
    for label, processor in load_phase1_processors().items():
        print(
            f"Processor {label}: {processor['num_qubits']} qubits, "
            f"{len(processor['coupling_map'])} coupling edges"
        )
