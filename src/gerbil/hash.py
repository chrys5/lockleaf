from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

def hash(key):
    """
    Hash a key using SHA256.

    Parameters:
        key(str): The key to hash.

    Returns:
        str: The hashed key.
    """
    key_hash = hashes.Hash(hashes.SHA256(), backend=default_backend())
    key_hash.update(key)
    key_hash = key_hash.finalize()
    return key_hash