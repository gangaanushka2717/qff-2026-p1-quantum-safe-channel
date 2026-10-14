
import os
import oqs

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

KEM_ALGORITHM = "ML-KEM-768"


def generate_recipient_keys():
    """Generate the recipient's ECDH and ML-KEM key pairs."""
    ecdh_private = ec.generate_private_key(ec.SECP256R1())
    ecdh_public_bytes = ecdh_private.public_key().public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    kem = oqs.KeyEncapsulation(KEM_ALGORITHM)
    kem_public_bytes = kem.generate_keypair()

    return ecdh_private, ecdh_public_bytes, kem, kem_public_bytes


def derive_hybrid_key(ecdh_secret, kem_secret, context):
    """Combine both shared secrets into a 256-bit session key."""
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"QFF-P1-hybrid-key-exchange-v1:" + context,
    ).derive(ecdh_secret + kem_secret)


def initiate_hybrid_exchange(recipient_ecdh_public_bytes,
                             recipient_kem_public_bytes):
    """Perform ephemeral ECDH and ML-KEM encapsulation."""
    recipient_ecdh_public = serialization.load_der_public_key(
        recipient_ecdh_public_bytes
    )

    ephemeral_private = ec.generate_private_key(ec.SECP256R1())
    ecdh_secret = ephemeral_private.exchange(
        ec.ECDH(), recipient_ecdh_public
    )

    ephemeral_public_bytes = ephemeral_private.public_key().public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    with oqs.KeyEncapsulation(KEM_ALGORITHM) as kem:
        kem_ciphertext, kem_secret = kem.encap_secret(
            recipient_kem_public_bytes
        )

    context = ephemeral_public_bytes + kem_ciphertext
    session_key = derive_hybrid_key(ecdh_secret, kem_secret, context)

    packet = {
        "ephemeral_ecdh_public": ephemeral_public_bytes,
        "kem_ciphertext": kem_ciphertext,
    }
    return packet, session_key


def complete_hybrid_exchange(packet, recipient_ecdh_private, recipient_kem):
    """Derive the same session key on the recipient side."""
    ephemeral_public = serialization.load_der_public_key(
        packet["ephemeral_ecdh_public"]
    )

    ecdh_secret = recipient_ecdh_private.exchange(
        ec.ECDH(), ephemeral_public
    )
    kem_secret = recipient_kem.decap_secret(packet["kem_ciphertext"])

    context = (
        packet["ephemeral_ecdh_public"] + packet["kem_ciphertext"]
    )
    return derive_hybrid_key(ecdh_secret, kem_secret, context)
