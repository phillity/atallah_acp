import numpy as np
import pandas as pd
from atallah import F, Enc, Dec
import hashlib
import os

'''
def set(security_param, graph):

    return pub, sec


def derive(graph, pub, v_src, v_dst, s_src):

    return found, k_dst
'''


if __name__ == "__main__":
    adjaceny_matrix = np.array([[1, 1, 1, 0], [0, 1, 0, 1], [0, 0, 1, 1], [0, 0, 0, 1]])
    df = pd.read_csv("breast-cancer.data")
    print("Objects: " + str(df.columns.values))

    # node i data
    s_i = hashlib.md5(os.urandom(16)).hexdigest()
    l_i = hashlib.md5(os.urandom(16)).hexdigest()
    t_i = F(s_i, l_i, val_opt="0")
    k_i = F(s_i, l_i, val_opt="1")

    # node j data
    s_j = hashlib.md5(os.urandom(16)).hexdigest()
    l_j = hashlib.md5(os.urandom(16)).hexdigest()
    t_j = F(s_j, l_j, val_opt="0")
    k_j = F(s_j, l_j, val_opt="1")

    # edge (i, j) data
    r_ij = F(t_i, l_j)
    y_ij = Enc(r_ij, t_j, k_j)

    # check it worked
    t_i = F(s_i, l_i, val_opt="0")
    r_ij = F(t_i, l_j)
    print(t_j)
    print(k_j)
    t_j, k_j = Dec(r_ij, y_ij)
    print(t_j)
    print(k_j)
