
import sys
import time
import tracemalloc
import statistics
import json
import csv
import hashlib
from pathlib import Path

import oqs

from secure_channel import (
    KEM_ALGORITHM,
    SIGNATURE_ALGORITHM,
    create_secure_message,
    receive_secure_message,
)

ROUNDS = 5
HANDSHAKE_ROUNDS = 20
PAYLOAD_SIZES = [1024, 100 * 1024, 10 * 1024 * 1024]


def run_benchmark():
    results = []
    handshake_times_ms = []
    handshake_peak_memory = 0

    
    with oqs.KeyEncapsulation(KEM_ALGORITHM) as kem:
        recipient_public_key = kem.generate_keypair()

        with oqs.Signature(SIGNATURE_ALGORITHM) as signer:
            signer.generate_keypair()
            for _ in range(HANDSHAKE_ROUNDS):
                tracemalloc.start()
                start = time.perf_counter()

                ciphertext, shared_secret = kem.encap_secret(
                    recipient_public_key
                )
                transcript = hashlib.sha256(
                    b"QFF-2026-benchmark" + recipient_public_key + ciphertext
                ).digest()
                signature = signer.sign(transcript)

                elapsed = (time.perf_counter() - start) * 1000
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()

                handshake_times_ms.append(elapsed)
                handshake_peak_memory = max(handshake_peak_memory, peak)
            handshake_summary = {
                "platform": "Local Windows computer",
                "measurement": "Sender-side ML-KEM encapsulation and ML-DSA signing",
                "rounds": HANDSHAKE_ROUNDS,
                "mean_time_ms": round(statistics.mean(handshake_times_ms), 3),
                "median_time_ms": round(statistics.median(handshake_times_ms), 3),
                "peak_traced_python_memory_bytes": handshake_peak_memory,
                "scope_note": "Not a complete two-peer or network handshake"
            }



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
                        packet,
                        recipient_kem,
                        recipient_public_key,
                        sender_public_key,
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
    (output / "handshake_benchmark.json").write_text(
        json.dumps(handshake_summary, indent=2),
         encoding="utf-8",
    )

    print(json.dumps(results, indent=2))
    print("\nSaved CSV and JSON in results/tables/")


if __name__ == "__main__":
    run_benchmark()
