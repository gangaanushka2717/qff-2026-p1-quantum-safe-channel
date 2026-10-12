
from src.processors import load_processor

processor_a = load_processor("processors/processor_A.json")
processor_b = load_processor("processors/processor_B.json")


for processor in [processor_a, processor_b]:
    print(f"\n{processor['name']}")
    print("Qubits:", processor["qubit_count"])
    print("Connections:", len(processor["coupling_map"]))
    print("Coupling map:", processor["coupling_map"])
    print("Noise model:", processor["noise_model"])
