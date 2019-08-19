import os
import numpy as np
import pandas as pd
from hashlib import md5
from acp import User, ACP
from dag import Node, Edge, DAG
from atallah import hash_fun, encrypt, decrypt
from Crypto.Cipher import AES


def encrypt_data(graph, dataset, node_object_map):
    for key, val in node_object_map.items():
        node = graph.node_list[key]
        k_i = node.get_k_i()
        aes = AES.new(bytes.fromhex(k_i), AES.MODE_EAX, nonce=bytes([42]))

        for col in val:
            data = dataset[val].values
            for i in range(data.shape[0]):
                data[i], _ = aes.encrypt_and_digest(data[i].encode())

    return dataset


if __name__ == "__main__":
    adjaceny_matrix = np.array([[1, 1, 1, 0],
                                [0, 1, 0, 1],
                                [0, 0, 1, 1],
                                [0, 0, 0, 1]])

    node_names = ["CEO", "Manager", "Team Lead", "Worker"]
    node_user_map = {}
    for node_name in node_names:
        users = [User(md5(os.urandom(4)).hexdigest(),
                 md5(os.urandom(16)).hexdigest()) for i in range(10)]
        node_user_map[node_name] = users

    graph = DAG(adjaceny_matrix, node_names, node_user_map)

    df = pf.read_csv("breast-cancer.data")
    print("Objects:" + str(df.columns.values))
    node_object_map = {}
    node_object_map["CEO"] = ["Object 1", "Object 2", "Object 3"]
    node_object_map["Manager"] = ["Object 4", "Object 5"]
    node_object_map["Team Lead"] = ["Object 6", "Object 7"]
    node_object_map["Worker"] = ["Object 8", "Object 9", "Object 10"]
    encrypted_dataset = encrypt_data(graph, df, node_object_map)



    '''
    acp_dict = {}
    roles = ["CEO", "Manager", "Team Lead", "Worker"]
    for role in roles:
        users = [User(md5(os.urandom(4)).hexdigest(),
                 md5(os.urandom(16)).hexdigest()) for i in range(10)]
        acp_dict[role] = ACP(role, users)
        # call node constructor here with role name and users (rather than ACP constructor)

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

    # testing DAG
    graph = DAG(adjaceny_matrix)
    graph.create_graph()
    # print the graph
    for key, node_obj in graph.node_list.items():
        print(f"{key}: {node_obj.edges.keys()}")
    '''
