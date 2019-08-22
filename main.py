import os
import numpy as np
import pandas as pd
import codecs
from copy import deepcopy
from hashlib import md5
from acp import User, ACP
from dag import Node, Edge, DAG
from atallah import hash_fun, encrypt, decrypt
from Crypto.Cipher import AES
import random
from decorators import timer


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


@timer
def decrypt_data_v1(
    graph, data, columns, source_node, target_col, node_object_map
):
    # Get node corresponding to column we want from mapping
    assert(target_col in columns)
    target_node = ""
    for node_name, cols in node_object_map.items():
        if target_col in cols:
            target_node = node_name
            break

    # Get path from source_node to target_node
    path = graph.get_path(source_node, target_node)
    if len(path) == 0:
        return None
    private_key = graph.derive_key(path)

    # Get encrypted data we want and intialize decrypted data
    col_idx = columns.index(target_col)
    encrypted_data = data[:, col_idx]
    decrypted_data = np.zeros(encrypted_data.shape).astype(str)

    # Decrypt data
    for i in range(encrypted_data.shape[0]):
        aes = AES.new(bytes.fromhex(private_key),
                      AES.MODE_EAX,
                      nonce=bytes([42]))
        cipher_text = encrypted_data[i]
        plain_text = aes.decrypt(bytes.fromhex(cipher_text)).decode()
        decrypted_data[i] = plain_text

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
                plain_text = codecs.encode(data[i, idx].encode(),
                                           "hex").decode()
                cipher_text, _ = (
                    aes.encrypt_and_digest(bytes.fromhex(k_i + plain_text))
                )
                data[i, idx] = cipher_text.hex()

    return data


@timer
def decrypt_data_v2(graph, data, columns, source_node, target_col):
    # Don't have node-to-object map, so get all descendant keys
    t_i = graph.node_list[source_node].get_t_i()
    private_keys = graph.derive_desc_key(source_node, t_i)

    # Get encrypted data we want and intialize decrypted data
    col_idx = columns.index(target_col)
    encrypted_data = data[:, col_idx]
    decrypted_data = np.zeros(encrypted_data.shape).astype(str)

    # Figure what key (if any) work
    target_key = None
    for private_key in private_keys:
        aes = AES.new(bytes.fromhex(private_key),
                      AES.MODE_EAX,
                      nonce=bytes([42]))
        cipher_text = encrypted_data[0]
        plain_text = aes.decrypt(bytes.fromhex(cipher_text)).hex()
        plain_text_key = plain_text[:len(private_key)]
        if private_key == plain_text_key:
            target_key = private_key
            break

    # Use working key to decrypt target_col data
    if target_key:
        for i in range(encrypted_data.shape[0]):
            aes = AES.new(bytes.fromhex(target_key),
                          AES.MODE_EAX,
                          nonce=bytes([42]))
            cipher_text = encrypted_data[i]
            plain_text = aes.decrypt(bytes.fromhex(cipher_text)).hex()
            plain_text_data = plain_text[len(private_key):]
            decrypted_data[i] = bytearray.fromhex(plain_text_data).decode()
    else:
        return None

    return decrypted_data


def create_random_dag(node_names, node_user_map):
    """
    Randomly generates a DAG graph. Start of by creating a list that represents the hierarchy.
    Each element in the list is another list showing the nodes in that level.
    The number of nodes in each level is random. Then use this hierarchy to create nodes
    and edges between nodes. Edges are created by randomly selecting a node in the previous level
    as a parent.

    Args:
        node_names (list): list of all the nodes to be used
        node_user_map (dict): use node name as a key to get all the users for node
    
    Returns:
        graph (DAG): returns a randomly generated DAG object
    """
    # the number of nodes to create will be the same as the length of the node_names list
    node_num = len(node_names)
    hierarchy = []
    curr_num_of_nodes = 0
    hierarchy.append([curr_num_of_nodes])
    curr_num_of_nodes += 1
    # create a hierarchy for the nodes
    while curr_num_of_nodes < node_num:
        nodes_to_create = random.choice(list(range(curr_num_of_nodes, node_num)))
        level = [i for i in range(curr_num_of_nodes, nodes_to_create+1)]
        curr_num_of_nodes += len(level)
        hierarchy.append(level)

    # create empty graph object without passing in input matrix
    graph = DAG(node_names, node_user_map)

    # use the hierarchy to create the nodes and edges
    for level in range(len(hierarchy)):
        if level == 0:
            graph.add_node(f"Node 0", node_user_map["Node 0"])
        else:
            for num in hierarchy[level]:
                curr_node_name = f"Node {num}"
                graph.add_node(curr_node_name, node_user_map[curr_node_name])
                parent_level = level-1
                # randomly choose a node a level above in the hierarchy as the parent
                parent_node_num = random.choice(hierarchy[parent_level])
                parent_node_name = f"Node {parent_node_num}"
                graph.add_edge(parent_node_name, curr_node_name)
    
    # for node in graph.node_list:
        # print(f"node: {node}, edges: {graph.node_list[node].edges.keys()}")
    return graph


if __name__ == "__main__":
    # Define number of nodes (and also number of objects)
    node_num = 4
    # Define number of user per node
    user_num = 100

    # Generate DAG adjaceny matrix for node_num nodes
    # adjaceny_matrix = np.array([[1, 1, 1, 0],
    #                             [0, 1, 0, 1],
    #                             [0, 0, 1, 1],
    #                             [0, 0, 0, 1]])

    # Create users for each node
    node_names = ["Node " + str(i) for i in range(node_num)]
    node_user_map = {}
    for node_name in node_names:
        users = [User(md5(os.urandom(4)).hexdigest(),
                 md5(os.urandom(16)).hexdigest()) for i in range(user_num)]
        node_user_map[node_name] = users

    # Create dataset with at least one column for each node
    df = pd.read_csv("breast-cancer.data")
    for i in range(df.shape[0]):
        for j in df.columns:
            if type(df.ix[i, j]) != str:
                df.ix[i, j] = str(df.ix[i, j])
    data = df.values
    copies = np.ceil(node_num / 10)
    if copies > 1:
        for i in range(copies):
            data = np.hstack([data, data])
    columns = ["Object " + str(i) for i in range(data.shape[1])]
    node_obj_li = np.array_split(np.array(columns), node_num)
    node_obj_li = [li.tolist() for li in node_obj_li]

    # Get node-to-object map for encryption and decryption_v1
    node_object_map = {}
    for i in range(node_num):
        node_object_map[node_names[i]] = node_obj_li[i]

    # create the graph randomly
    graph = create_random_dag(node_names, node_user_map)

    # Get random target column to decrypt
    target_col = np.random.choice(columns)
    # Get random source node
    source_node = np.random.choice(node_names)
    # Ensure random source node can actually decrypt the random target column
    compatible = False
    while not compatible:
        target_node = ""
        for node_name, cols in node_object_map.items():
            if target_col in cols:
                target_node = node_name
                break
        path = graph.get_path(source_node, target_node)
        if len(path) > 0:
            compatible = True
        else:
            target_col = np.random.choice(columns)



    # Method 1
    encrypted_data = encrypt_data_v1(
        graph, deepcopy(data), columns, node_object_map
    )
    # Time this function
    decrypted_data = decrypt_data_v1(
        graph,
        encrypted_data,
        columns, source_node,
        target_col,
        node_object_map
    )

    # Method 2
    encrypted_data_v2 = encrypt_data_v2(
        graph, deepcopy(data), columns, node_object_map
    )
    # Time this function
    decrypted_data_v2 = decrypt_data_v2(
        graph, encrypted_data_v2, columns, source_node, target_col
    )
