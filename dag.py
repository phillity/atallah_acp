from atallah import F, Enc, Dec
import hashlib
import os

"""
Notes about notation:

public:
    l_i: node label
    y_ij: edge label

private:
    s_i: random secret value
    t_i: derive key
    k_i: decrypt key
    r_ij: edge seed
"""


class Node:
    def __init__(self, name):
        """
        Constructor for node. Will use urandom and md5 hash to generate node
        label (l_i) and secret value (__s_i). Each node contains a list of all
        the edges to it's child nodes.

        Args:
            name (string): name to identify node

        Returns:
            N/A
        """
        self.l_i = hashlib.md5(os.urandom(16)).hexdigest()
        self.__s_i = hashlib.md5(os.urandom(16)).hexdigest()
        self.edges = []
        self.name = name

    def get_t_i(self):
        """
        Returns the value of the derive key (t_i).

        Args:
            N/A

        Returns:
            hex digest(string): hash of __s_i + "0" + l_i
        """
        # t_i = F_s_i(0||l_i)
        return F(self.__s_i, self.l_i, val_opt="0")

    def get_k_i(self):
        """
        Returns the value of the decrypt key (k_i).

        Args:
            N/A

        Returns:
            hex digest(string): hash of __si_i + "1" + l_i
        """
        # k_i = F_s_i(1||l_i)
        return F(self.__s_i, self.l_i, val_opt="1")


class Edge:
    def __init__(self, t_i, l_j, t_j, k_j):
        """
        Constructor for edge. Given the parent derive key, child label, child derive key and
        child decrypt key the edge will calculate the edge seed and the edge label.

        Args:
            t_i(string): hex string of parent derive key 
            l_j(string): hex string of child label
            t_j(string): hex string of child dervive key
            k_j(string): hex string of child decrypt key

        Returns:
            N/A
        """
        # r_ij = F_ti(l_j)
        self.__r_ij = F(t_i, l_j)
        # y_ij = Enc_r_ij(t_j||k_j)
        self.y_ij = Enc(r_ij, t_j, k_j)


class DAG:
    def __init__(self, input_matrix):
        """
        Constructor for DAG. Takes 

        Args:

        Returns:
            N/A
        """
        self.node_list = {}
        self.input_matrix = input_matrix
    
    def add_node(self, name):
        self.node_list[name] = Node(name)

    def add_edge(self, paren_node, child_node):
        paren = self.node_list[paren_node]
        child = self.node_list[child_node]

        new_edge = Edge(paren.get_t_i(), child.l_i, child.get_t_i(), child.get_k_i())

        self.node_list[paren_node].edges[child_node] = new_edge

    def create_graph(self):
        for i in range(len(self.input_matrix)):
            add_node(str(i))
            
        for i in range(len(self.input_matrix)):
            for j in range(len(self.input_matrix[i])):
                add_edge(str(i), str(j))

    def have_path(self, src_node, des_node):
        if src_node == des_node:
            return True
        for nodes in self.node_list[src_node].edges.keys():
            if self.havePath(nodes, des_node):
                return True
        return False


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


def descendant(self, v_i):
    """
    Find all v_j s.t. there is a path from v_i to v_j.

    Args:
        v_i (Node): Node to find descendants of.
        graph (np.ndarray): Adjacency matrix of DAG.

    Returns:
        v_j (list): List of descendant nodes of v_i.
    """

    desc = []
    for node in self.node_list.keys():
        if (node not in desc) and (self.havePath(v_i, node)):
            desc.append(node)
    return desc


def predecessor(v_i):
    """
    Find all v_j s.t. there is a directed edge connecting v_j to v_i.

    Args:
        v_i (Node): Node to find predecessors of.
        graph (np.ndarray): Adjacency matrix of DAG.

    Returns:
        v_j (list): List of predecessor nodes of v_i.
    """

    pred = []
    for node in self.node_list.keys():
        if (node not in pred) and (node in self.node_list[v_i].edges):
            pred.append(node)
    return pred



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