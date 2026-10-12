# QFF 2026 Phase 1 — Quantum-Safe Secure Channel

A prototype secure messaging channel using post-quantum cryptographic algorithms for key establishment, authentication, key derivation, and authenticated encryption.

## Project Overview

This project explores a quantum-safe secure channel using:

- **ML-KEM-768 (FIPS 203):** Establishes a shared secret.
- **ML-DSA-65 (FIPS 204):** Authenticates the sender using a digital signature.
- **HKDF-SHA-256:** Derives a 256-bit symmetric key.
- **AES-256-GCM:** Encrypts and authenticates message contents.

The prototype includes a local sender/receiver demonstration, tampering checks, payload benchmarks, and a topology comparison of the supplied Processor A and Processor B configurations.

## Repository Structure

```text
processors/       Processor A, Processor B, and proposed Platform D metadata
src/              Secure-channel implementation and benchmark scripts
results/tables/   Benchmark results in CSV and JSON formats
main.py           Processor configuration summary
quantum_test.py   Quantum-related test script
report.md         Project report, protocol flow, and analysis
requirements.txt  Python dependencies
```

## Local Benchmark Results

## Local Benchmark Results

The local software prototype was tested with payloads of 1 KB, 100 KB, and 10 MB over five rounds per size.

| Payload | Mean round-trip time | Correctness |
|---|---:|---|
| 1 KB | 13.133 ms | Passed |
| 100 KB | 9.824 ms | Passed |
| 10 MB | 43.839 ms | Passed |

These timings measure a local cryptographic round trip, not network latency or quantum-processor execution. See `results/tables/local_benchmark.csv` for additional metrics. Results may vary between runs.


## Processor Topology Analysis

The supplied configurations describe:

- **Processor A:** 5 qubits and 4 coupling connections.
- **Processor B:** 9 qubits and 12 coupling connections.

The comparison is based on topology only. Basis-gate and noise-model information is unavailable, so no gate-level performance or fidelity conclusions are claimed.

## Running the Prototype

Use Python 3.13.5 or a compatible environment, install the required dependencies, and ensure the native `liboqs` library is installed and discoverable by your system.

Run the secure-channel test from the repository root in PowerShell:

```powershell
$env:PATH = "$env:TEMP\liboqs-install\bin;$env:PATH"
$env:PYTHONPATH = "$PWD\src"
.\.venv\Scripts\python.exe src\test_secure_channel.py
```

The `liboqs` path above is specific to the local Windows setup and may need to be changed on another machine.

## Limitations

- Platform D is a proposed local software benchmark environment; its definition has not been confirmed by the organizers.
- Processor A/B topology analysis and local software cryptographic benchmarks are separate experiments.
- The current prototype is not a production-ready network protocol. Trusted public-key distribution and stronger binding of peer identities and protocol context require further work.
- Benchmark measurements were collected locally and should not be interpreted as results from quantum hardware.

## Status

Prototype implemented; local correctness and tampering tests passed. Further protocol hardening and confirmation of the official Platform A/B/D benchmark requirements remain necessary.