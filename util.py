from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend
import numpy as np

def generate_keys():
    """
    Generates compatible private and public keys

    Input: None
    Output: (generated public key, generated private key)
    """
    key = rsa.generate_private_key(
        backend=crypto_default_backend(),
        public_exponent=65537,
        key_size=2048
    )

    private_key = key.private_bytes(
        crypto_serialization.Encoding.PEM,
        crypto_serialization.PrivateFormat.PKCS8,
        crypto_serialization.NoEncryption()
    )

    public_key = key.public_key().public_bytes(
        crypto_serialization.Encoding.OpenSSH,
        crypto_serialization.PublicFormat.OpenSSH
    )

    return public_key, private_key

def exponential_latency(mapping):
    """
    Generates a function to calculate latencies from a Poisson distribution between two nodes
    """
    def calcuate_latency(start, end):
        if (start, end) not in mapping and (end, start) not in mapping:
            return np.random.poisson(500)
        
        if (start, end) in mapping:
            return np.random.poisson(mapping[(start, end)])
        if (end, start) in mapping:
            return np.random.poisson(mapping[(end, start)])
    return calcuate_latency