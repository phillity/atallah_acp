import os
import numpy as np
import pandas as pd
import codecs
from hashlib import md5
from acp import User, ACP
from dag import Node, Edge, DAG
from atallah import hash_fun, encrypt, decrypt
from Crypto.Cipher import AES


def encrypt_data_v1(graph, data, columns, node_object_map):
    for node_name, objects in node_object_map.items():
        node = graph.node_list[node_name]
        k_i = node.get_k_i()

        for obj in objects:
            idx = columns.index(obj)
            for i in range(data[:, idx].shape[0]):
                aes = AES.new(bytes.fromhex(k_i),
                              AES.MODE_EAX,
                              nonce=bytes([42]))
                plain_text = codecs.encode(data[i, idx].encode(),
                                           "hex").decode()
                cipher_text, _ = (
                    aes.encrypt_and_digest(bytes.fromhex(plain_text))
                )
                data[i, idx] = cipher_text.hex()

    return data


def decrypt_data_v1(graph, data, columns, source_node, target_node, node_object_map):
    path = graph.get_path(source_node, target_node, [])
    private_key = graph.derive_key(path)

    objects = node_object_map[target_node]
    decrypted_data = np.zeros((data.shape[0], len(objects))).astype(str)

    for j, obj in enumerate(objects):
        idx = columns.index(obj)
        for i in range(data[:, idx].shape[0]):
            aes = AES.new(bytes.fromhex(private_key),
                          AES.MODE_EAX,
                          nonce=bytes([42]))
            cipher_text = data[i, idx]
            plain_text = aes.decrypt(bytes.fromhex(cipher_text)).decode()
            decrypted_data[i, j] = plain_text

    return decrypted_data


def encrypt_data_v2(graph, data, columns, node_object_map):
    for node_name, objects in node_object_map.items():
        node = graph.node_list[node_name]
        k_i = node.get_k_i()

        for obj in objects:
            idx = columns.index(obj)
            for i in range(data[:, idx].shape[0]):
                aes = AES.new(bytes.fromhex(k_i),
                              AES.MODE_EAX,
                              nonce=bytes([42]))
                concatted_data = k_i + data[i, idx]
                plain_text = codecs.encode(concatted_data.encode(),
                                           "hex").decode()
                cipher_text, _ = (
                    aes.encrypt_and_digest(bytes.fromhex(plain_text))
                )
                data[i, idx] = cipher_text.hex()

    return data


def decrypt_data_v2(graph, data, columns, source_node, num_of_objects):
    t_i = graph.node_list[source_node].get_t_i()
    private_keys = graph.derive_desc_key(source_node, t_i)

    decrypted_data = np.zeros((data.shape[0], num_of_objects)).astype(str)

    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            for private_key in private_keys:
                aes = AES.new(bytes.fromhex(private_key),
                              AES.MODE_EAX,
                              nonce=bytes([42]))
                cipher_text = data[i, j]
                plain_text = aes.decrypt(bytes.fromhex(cipher_text))
                print(f"plain_text: {plain_text}")
                plain_text = plain_text.decode()
                plain_text_key = plain_text[:len(private_key)]
                plain_text_data = plain_text[len(private_key):]
                if private_key == plain_text_key:
                    decrypted_data[i, j] = plain_text_data


    return decrypted_data

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

    df = pd.read_csv("breast-cancer.data")
    for i in range(df.shape[0]):
        for j in df.columns:
            if type(df.ix[i, j]) != str:
                df.ix[i, j] = str(df.ix[i, j])

    columns = df.columns.values.tolist()
    data = df.values

    print("Objects:" + str(columns))
    node_object_map = {}
    node_object_map["CEO"] = ["Object 1", "Object 2", "Object 3"]
    node_object_map["Manager"] = ["Object 4", "Object 5"]
    node_object_map["Team Lead"] = ["Object 6", "Object 7"]
    node_object_map["Worker"] = ["Object 8", "Object 9", "Object 10"]
    # encrypted_dataset = encrypt_data_v1(graph, data, columns, node_object_map)
    # decrypted_dataset = decrypt_data_v1(graph, data, columns, "CEO", "Manager", node_object_map)
    encrypted_dataset_v2 = encrypt_data_v2(graph, data, columns, node_object_map)
    decrypted_dataset_v2 = decrypt_data_v2(graph, data, columns, "CEO", len(node_object_map))



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
