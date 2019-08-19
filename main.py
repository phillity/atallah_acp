import os
import numpy as np
import pandas as pd
from hashlib import md5
from acp import User, ACP
from atallah import hash_fun, encrypt, decrypt


if __name__ == "__main__":
    '''
    adjaceny_matrix = np.array([[1, 1, 1, 0],
                                [0, 1, 0, 1],
                                [0, 0, 1, 1],
                                [0, 0, 0, 1]])
    df = pd.read_csv("breast-cancer.data")
    print("Objects: " + str(df.columns.values))
    '''

    acp_dict = {}
    roles = ["CEO", "Manager", "Team Lead", "Worker"]
    for role in roles:
        users = [User(md5(os.urandom(4)).hexdigest(),
                 md5(os.urandom(16)).hexdigest()) for i in range(10)]
        acp_dict[role] = ACP(role, users)

    # CEO node data
    SID_i = acp_dict["CEO"].users[0].get_SID()
    s_i = acp_dict["CEO"].evaluate_polynomial(SID_i)
    for user in acp_dict["CEO"].users:
        SID_j = user.get_SID()
        assert(s_i == acp_dict["CEO"].evaluate_polynomial(SID_j))
    l_i = md5(os.urandom(16)).hexdigest()
    t_i = hash_fun(s_i, l_i, val_opt="0")
    k_i = hash_fun(s_i, l_i, val_opt="1")

    # Manager node data
    SID_i = acp_dict["Manager"].users[0].get_SID()
    s_j = acp_dict["Manager"].evaluate_polynomial(SID_i)
    for user in acp_dict["Manager"].users:
        SID_j = user.get_SID()
        assert(s_j == acp_dict["Manager"].evaluate_polynomial(SID_j))
    l_j = md5(os.urandom(16)).hexdigest()
    t_j = hash_fun(s_j, l_j, val_opt="0")
    k_j = hash_fun(s_j, l_j, val_opt="1")

    # edge (CEO, Manager) data
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
