import hashlib
import numpy as np
import pandas as pd


def ancestory(v_i, graph):
    """
    Find all v_j s.t. there is a path from v_j to v_i.

    Args:
        v_i (Node): Node to find ancestors of.
        graph (np.ndarray): Adjacency matrix of DAG.

    Returns:
        v_j (list): List of ancestor nodes of v_i.
    """

    return v_j


def descendant(v_i, graph):
    """
    Find all v_j s.t. there is a path from v_i to v_j.

    Args:
        v_i (Node): Node to find descendants of.
        graph (np.ndarray): Adjacency matrix of DAG.

    Returns:
        v_j (list): List of descendant nodes of v_i.
    """

    return v_j


def predecessor(v_i, graph):
    """
    Find all v_j s.t. there is a directed edge connecting v_j to v_i.

    Args:
        v_i (Node): Node to find predecessors of.
        graph (np.ndarray): Adjacency matrix of DAG.

    Returns:
        v_j (list): List of predecessor nodes of v_i.
    """

    return v_j


def successor(v_i, graph):
    """
    Find all v_j s.t. there is a directed edge connecting v_i to v_j.

    Args:
        v_i (Node): Node to find successors of.
        graph (np.ndarray): Adjacency matrix of DAG.

    Returns:
        v_j (list): List of successor nodes of v_i.
    """

    return v_j

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
