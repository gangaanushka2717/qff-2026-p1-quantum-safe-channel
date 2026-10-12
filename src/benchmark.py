
import sys
import time
import tracemalloc
import statistics
import json
import csv
from pathlib import Path

import oqs

from secure_channel import (
    KEM_ALGORITHM,
    SIGNATURE_ALGORITHM,
    create_secure_message,
    receive_secure_message,
)

ROUNDS = 5
PAYLOAD_SIZES = [1024, 100 * 1024, 10 * 1024 * 1024]


def run_benchmark():
    results = []

    with oqs.KeyEncapsulation(KEM_ALGORITHM) as recipient_kem:
        recipient_public_key = recipient_kem.generate_keypair()

        with oqs.Signature(SIGNATURE_ALGORITHM) as signer:
            sender_public_key = signer.generate_keypair()

            for size in PAYLOAD_SIZES:
                payload = "X" * size
                times_ms = []
                peak_memory = 0
                packet_bytes = 0

                for _ in range(ROUNDS):
                    tracemalloc.start()
                    start = time.perf_counter()

                    packet = create_secure_message(
                        payload, recipient_public_key, signer
                    )
                    received = receive_secure_message(
                        packet, recipient_kem, sender_public_key
                    )

                    elapsed = (time.perf_counter() - start) * 1000
                    _, peak = tracemalloc.get_traced_memory()
                    tracemalloc.stop()

                    if received != payload:
                        raise RuntimeError("Correctness check failed")

                    times_ms.append(elapsed)
                    peak_memory = max(peak_memory, peak)
                    packet_bytes = sum(
                        len(value)
                        for value in packet.values()
                        if isinstance(value, bytes)
                    )

                results.append({
                    "platform": "Local Windows computer",
                    "KEM": KEM_ALGORITHM,
                    "Signature": SIGNATURE_ALGORITHM,
                    "payload_bytes": size,
                    "rounds": ROUNDS,
                    "mean_round_trip_ms": round(
                        statistics.mean(times_ms), 3
                    ),
                    "median_round_trip_ms": round(
                        statistics.median(times_ms), 3
                    ),
                    "peak_traced_python_memory_bytes": peak_memory,
                    "packet_bytes": packet_bytes,
                    "correctness": "passed",
                })

    output = Path("results/tables")
    output.mkdir(parents=True, exist_ok=True)

    with (output / "local_benchmark.csv").open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file, fieldnames=results[0].keys()
        )
        writer.writeheader()
        writer.writerows(results)

    (output / "local_benchmark.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )

    print(json.dumps(results, indent=2))
    print("\nSaved CSV and JSON in results/tables/")


if __name__ == "__main__":
    run_benchmark()
