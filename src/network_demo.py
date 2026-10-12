
import json
import socket
import threading
import base64

import oqs
from secure_channel import (
    KEM_ALGORITHM,
    SIGNATURE_ALGORITHM,
    create_secure_message,
    receive_secure_message,
)


HOST = "127.0.0.1"
PORT = 0
MESSAGE = "Hello through our quantum-safe TCP channel!"


def encode_bytes(value):
    return base64.b64encode(value).decode("ascii")


def decode_bytes(value):
    return base64.b64decode(value, validate=True)


def send_packet(connection, packet):
    raw = json.dumps(packet).encode("utf-8")
    connection.sendall(len(raw).to_bytes(4, "big") + raw)


def receive_packet(connection):
    header = connection.recv(4)
    if len(header) != 4:
        raise ConnectionError("Missing packet length")

    length = int.from_bytes(header, "big")
    if length > 12 * 1024 * 1024:
        raise ValueError("Packet too large")

    data = bytearray()
    while len(data) < length:
        chunk = connection.recv(length - len(data))
        if not chunk:
            raise ConnectionError("Incomplete packet")
        data.extend(chunk)

    return json.loads(data.decode("utf-8"))


def main():
    with oqs.KeyEncapsulation(KEM_ALGORITHM) as recipient_kem:
        recipient_public_key = recipient_kem.generate_keypair()

        with oqs.Signature(SIGNATURE_ALGORITHM) as signer:
            sender_public_key = signer.generate_keypair()
            errors = []

            with socket.socket() as server:
                server.bind((HOST, PORT))
                server.listen(1)
                port = server.getsockname()[1]

                def receiver():
                    try:
                        with server.accept()[0] as connection:
                            send_packet(connection, {
                                "recipient_public_key":
                                    encode_bytes(recipient_public_key)
                            })

                            packet = receive_packet(connection)
                            packet = {
                                key: decode_bytes(value)
                                for key, value in packet.items()
                            }

                            message = receive_secure_message(
                                packet,
                                recipient_kem,
                                recipient_public_key,
                                sender_public_key,
                            )
                            print("Receiver got:", message)
                    except Exception as error:
                        errors.append(error)

                thread = threading.Thread(
                    target=receiver, daemon=True
                )
                thread.start()

                with socket.create_connection((HOST, port)) as client:
                    public_data = receive_packet(client)
                    public_key = decode_bytes(
                        public_data["recipient_public_key"]
                    )

                    packet = create_secure_message(
                        MESSAGE, public_key, signer
                    )
                    send_packet(client, {
                        key: encode_bytes(value)
                        for key, value in packet.items()
                    })

                thread.join(timeout=10)

            if errors:
                raise RuntimeError(
                    "TCP receiver failed"
                ) from errors[0]

            print("Sender sent:", MESSAGE)
            print("TCP demo: PASSED")


if __name__ == "__main__":
    main()
