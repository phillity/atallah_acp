import hashlib
from Crypto.Cipher import AES
import binascii


def F(val_1, val_2, val_opt=None):
    """
    Concats values and hashes using md5.

    Args:
        val_1 (string): The first value to hash
        val_2 (string): Second value to hash
        val_opt (string): None by default, but should be able to pass in either "0" or "1" to be concated between values

    Returns:
        hex digest (string): the resulting hash
    """
    message = ""

    if val_opt:
        message = val_1 + val_opt + val_2
    else:
        message = val_1 + val_2

    return hashlib.md5(message.encode('utf-8')).hexdigest()


def Enc(r_ij, t_j, k_j):
    y_ij = int(r_ij + r_ij, 16) ^ int(t_j + k_j, 16)
    return format(y_ij, 'x').zfill(64)


def Dec(r_ij, y_ij):
    t_j_and_k_j = int(r_ij + r_ij, 16) ^ int(y_ij, 16)
    t_j_and_k_j = format(t_j_and_k_j, 'x').zfill(64)
    t_j = t_j_and_k_j[:32]
    k_j = t_j_and_k_j[32:]
    return t_j, k_j
