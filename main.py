import os
import numpy as np
import pandas as pd
from atallah import hash_fun, encrypt, decrypt
from hashlib import md5


if __name__ == "__main__":
    adjaceny_matrix = np.array([[1, 1, 1, 0],
                                [0, 1, 0, 1],
                                [0, 0, 1, 1],
                                [0, 0, 0, 1]])
    df = pd.read_csv("breast-cancer.data")
    print("Objects: " + str(df.columns.values))

    # node i data
    s_i = md5(os.urandom(16)).hexdigest()
    l_i = md5(os.urandom(16)).hexdigest()
    t_i = hash_fun(s_i, l_i, val_opt="0")
    k_i = hash_fun(s_i, l_i, val_opt="1")

    # node j data
    s_j = md5(os.urandom(16)).hexdigest()
    l_j = md5(os.urandom(16)).hexdigest()
    t_j = hash_fun(s_j, l_j, val_opt="0")
    k_j = hash_fun(s_j, l_j, val_opt="1")

    # edge (i, j) data
    r_ij = hash_fun(t_i, l_j)
    y_ij = encrypt(r_ij, t_j, k_j)

    # check it worked
    t_i = hash_fun(s_i, l_i, val_opt="0")
    r_ij = hash_fun(t_i, l_j)
    print(t_j)
    print(k_j)

    t_j, k_j = decrypt(r_ij, y_ij)
    print(t_j)
    print(k_j)
