import csv
import json
import os
import statistics
import time
import tracemalloc
import hmac
from pathlib import Path

from hybrid_exchange import (
    generate_recipient_keys,
    initiate_hybrid_exchange,
    complete_hybrid_exchange,
)

ROUNDS = 20
ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results" / "tables"
RESULTS.mkdir(parents=True, exist_ok=True)

def main():
    ec_private, ec_public, kem, kem_public = generate_recipient_keys()
    times_ms = []
    packet_sizes = []
    peak_memory = 0

    try:
        # Warm-up run, excluded from measurements
        packet, sender_key = initiate_hybrid_exchange(ec_public, kem_public)
        receiver_key = complete_hybrid_exchange(packet, ec_private, kem)
        assert hmac.compare_digest(sender_key, receiver_key)

        for _ in range(ROUNDS):
            tracemalloc.start()
            start = time.perf_counter()

            packet, sender_key = initiate_hybrid_exchange(
                ec_public, kem_public
            )
            receiver_key = complete_hybrid_exchange(
                packet, ec_private, kem
            )

            elapsed_ms = (time.perf_counter() - start) * 1000
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            assert hmac.compare_digest(sender_key, receiver_key)
            times_ms.append(elapsed_ms)
            packet_sizes.append(
                len(packet["ephemeral_ecdh_public"])
                + len(packet["kem_ciphertext"])
            )
            peak_memory = max(peak_memory, peak)

        result = {
            "benchmark": "ECDH-P256 + ML-KEM-768 hybrid exchange",
            "environment": "Local Windows computer",
            "rounds": ROUNDS,
            "mean_latency_ms": statistics.mean(times_ms),
            "median_latency_ms": statistics.median(times_ms),
            "min_latency_ms": min(times_ms),
            "max_latency_ms": max(times_ms),
            "exchange_packet_bytes": statistics.mean(packet_sizes),
            "ephemeral_ecdh_public_bytes": len(packet["ephemeral_ecdh_public"]),
            "ml_kem_ciphertext_bytes": len(packet["kem_ciphertext"]),
            "peak_traced_python_memory_bytes": peak_memory,
            "key_match_verified": True,
            "notes": (
                "Local round-trip measurement; excludes recipient key "
                "generation, network overhead, and production authentication. "
                "Tracemalloc does not measure total process RAM."
            ),
        }

        (RESULTS / "hybrid_benchmark.json").write_text(
            json.dumps(result, indent=2), encoding="utf-8"
        )
        with (RESULTS / "hybrid_benchmark.csv").open(
            "w", newline="", encoding="utf-8"
        ) as f:
            writer = csv.DictWriter(f, fieldnames=result.keys())
            writer.writeheader()
            writer.writerow(result)

        print(json.dumps(result, indent=2))
        print("Saved hybrid benchmark CSV and JSON.")
    finally:
        kem.free()

if __name__ == "__main__":
    main()
