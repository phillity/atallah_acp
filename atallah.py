from hashlib import md5
from Crypto.Cipher import AES
"""
'Dynamic and Efficient Key Management for Access Hierarchies'
M. Atallah, et. al.
https://dl.acm.org/citation.cfm?id=1455531
"""


def hash_fun(val_1, val_2, val_opt=None):
    """
    Concats values and hashes using MD5. \\
    hash = hash_fun(val_1||val_opt||val_2)

    Args:
        val_1 (string): 16 byte hex value to hash.
        val_2 (string): 16 byte hex value to hash.
        val_opt (string): None by default, but should be able to pass in either
                          "0" or "1" to be concated between values.

    Returns:
        hex digest (string): the resulting hash.
    """
    if val_1.startswith("0x"):
        val_1 = val_1[2:]
    if val_2.startswith("0x"):
        val_2 = val_2[2:]

    message = ""
    if val_opt:
        message = val_1 + val_opt + val_2
    else:
        message = val_1 + val_2

    return md5(message.encode("utf-8")).hexdigest()


def encrypt(r_ij, t_j, k_j, nonce=bytes([42])):
    """
    AES encryption of t_j||k_j using r_ij key and nonce. \\
    y_ij = AES.encrypt{r_ij}(t_j||k_j)

    Args:
        r_ij (string): 16 byte hex value to use as AES key.
        t_j (string): 16 byte t_j value.
        k_j (string): 16 byte k_j value.
        nonce (bytes): bytes([42]) by default, byte array nonce for AES.

    Returns:
        y_ij (string): 32 byte ecryption.
    """
    aes = AES.new(bytes.fromhex(r_ij), AES.MODE_EAX, nonce=nonce)
    y_ij, _ = aes.encrypt_and_digest(bytes.fromhex(t_j + k_j))

    return y_ij.hex()


def decrypt(r_ij, y_ij, nonce=bytes([42])):
    """
    AES decryption of y_ij using r_ij key and nonce. \\
    t_j||k_j = AES.decrypt{r_ij}(r_ij)

    Args:
        r_ij (string): 16 byte hex value to use as AES key.
        y_ij (string): 32 byte ecryption of t_j||k_j using r_ij key and nonce.
        nonce (bytes): bytes([42]) by default, byte array nonce for AES.

    Returns:
        t_j (string): 16 byte t_j value.
        k_j (string): 16 byte k_j value.
    """
    aes = AES.new(bytes.fromhex(r_ij), AES.MODE_EAX, nonce=nonce)
    t_j_and_k_j = aes.decrypt(bytes.fromhex(y_ij)).hex()

    t_j = t_j_and_k_j[:32]
    k_j = t_j_and_k_j[32:]

    return t_j, k_j


"""
def set(security_param, graph):

    return pub, sec


def derive(graph, pub, v_src, v_dst, s_src):

    return found, k_dst
"""
