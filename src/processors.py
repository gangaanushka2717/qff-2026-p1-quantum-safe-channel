
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_processor(path):
    """Load a processor configuration from a JSON file."""
    processor_path = Path(path)

    if not processor_path.is_absolute():
        processor_path = PROJECT_ROOT / processor_path

    with processor_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_phase1_processors():
    """Load both Phase 1 processor reference configurations."""
    return {
        "A": load_processor("processors/processor_A.json"),
        "B": load_processor("processors/processor_B.json"),
    }


if __name__ == "__main__":
    for label, processor in load_phase1_processors().items():
        print(
            f"Processor {label}: "
            f"{processor.get('num_qubits', processor.get('qubit_count'))} qubits, "
            f"{len(processor['coupling_map'])} coupling edges"
        )
