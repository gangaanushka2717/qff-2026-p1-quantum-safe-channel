
import oqs
import os
import time
import hashlib

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


KEM_ALGORITHM = "ML-KEM-768"
SIGNATURE_ALGORITHM = "ML-DSA-65"


def derive_key(shared_secret, transcript):
    """Derive a 256-bit AES key from the KEM shared secret."""
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"QFF-2026-secure-channel:" + transcript,
    ).derive(shared_secret)


def create_secure_message(message, recipient_public_key, sender_signer):
    """Create an authenticated, encrypted message for a recipient."""
    with oqs.KeyEncapsulation(KEM_ALGORITHM) as kem:
        ciphertext, shared_secret = kem.encap_secret(recipient_public_key)

    nonce = os.urandom(12)
    transcript = hashlib.sha256(
    b"QFF-2026-secure-channel-v2"
    + recipient_public_key
    + ciphertext
    + nonce
).digest()

    signature = sender_signer.sign(transcript)
    key = derive_key(shared_secret, transcript)

    encrypted_message = AESGCM(key).encrypt(
        nonce, message.encode("utf-8"), transcript
    )

    return {
        "kem_ciphertext": ciphertext,
        "nonce": nonce,
        "transcript": transcript,
        "signature": signature,
        "encrypted_message": encrypted_message,
    }


def receive_secure_message(
    packet,
    recipient_kem,
    recipient_public_key,
    trusted_sender_public_key,
):
    """Verify the sender's signature, then decrypt the message."""

    transcript = packet["transcript"]

    # Verify the signature before accepting the message.
    with oqs.Signature(SIGNATURE_ALGORITHM) as verifier:
        is_valid = verifier.verify(
            transcript,
            packet["signature"],
            trusted_sender_public_key,
        )

    if not is_valid:
        raise ValueError("Sender authentication failed!")

    # Confirm the transcript matches the packet contents.
    expected_transcript = hashlib.sha256(
    b"QFF-2026-secure-channel-v2"
    + recipient_public_key
    + packet["kem_ciphertext"]
    + packet["nonce"]
).digest()

    if transcript != expected_transcript:
        raise ValueError("Message transcript was modified!")

    # Decapsulate the KEM ciphertext to recover the shared secret.
    shared_secret = recipient_kem.decap_secret(packet["kem_ciphertext"])
    key = derive_key(shared_secret, transcript)

    plaintext = AESGCM(key).decrypt(
        packet["nonce"],
        packet["encrypted_message"],
        transcript,
    )

    return plaintext.decode("utf-8")
