
import oqs

from secure_channel import (
    KEM_ALGORITHM,
    SIGNATURE_ALGORITHM,
    create_secure_message,
    receive_secure_message,
)

message = "Hello from our QFF 2026 quantum-safe channel!"

with oqs.KeyEncapsulation(KEM_ALGORITHM) as recipient_kem:
    recipient_public_key = recipient_kem.generate_keypair()

    with oqs.Signature(SIGNATURE_ALGORITHM) as sender_signer:
        sender_public_key = sender_signer.generate_keypair()

        packet = create_secure_message(
            message, recipient_public_key, sender_signer
        )

        received_message = receive_secure_message(
            packet,
            recipient_kem,
            recipient_public_key,
            sender_public_key,
        )

        print("Original message:", message)
        print("Received message:", received_message)
        print("Successful match:", message == received_message)

        # Test whether a modified encrypted message is rejected.
        tampered_packet = dict(packet)
        altered = bytearray(tampered_packet["encrypted_message"])
        altered[0] ^= 1
        tampered_packet["encrypted_message"] = bytes(altered)

        try:
            receive_secure_message(
                tampered_packet,
                recipient_kem,
                recipient_public_key,
                sender_public_key,
            )
            print("Tampering test: FAILED")
        except Exception:
            print("Tampering test: PASSED — modified message rejected")

        # Test whether an altered signature is rejected.
        bad_signature_packet = dict(packet)
        altered_signature = bytearray(bad_signature_packet["signature"])
        altered_signature[0] ^= 1
        bad_signature_packet["signature"] = bytes(altered_signature)

        try:
            receive_secure_message(
                bad_signature_packet,
                recipient_kem,
                recipient_public_key,
                sender_public_key,
            )
            print("Signature test: FAILED")
        except Exception:
            print("Signature test: PASSED — invalid signature rejected")
