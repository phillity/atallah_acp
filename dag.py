import os
import hashlib
from hashlib import md5
from acp import User, ACP
from atallah import hash_fun, encrypt, decrypt


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
    def __init__(self, name, users):
        """
        Constructor for node. Will use urandom and md5 hash to generate node
        label (l_i) and secret value (s_i). Each node contains a list of all
        the edges to it's child nodes.

        Args:
            name (string): name to identify node
            users (list): list of users assigned to node at initialization

        Returns:
            N/A
        """
        self.name = name
        self.users = users
        self.l_i = md5(os.urandom(16)).hexdigest()
        self.__s_i = md5(os.urandom(16)).hexdigest()
        self.acp = ACP(self.__s_i)
        self.edges = {}

    def update_secret(self):
        self.__s_i = md5(os.urandom(16)).hexdigest()
        self.acp = ACP(self.__s_i)

    def get_t_i(self):
        """
        Returns the value of the derive key (t_i).

        Args:
            N/A

        Returns:
            hex digest (string): hash of s_i + "0" + l_i
        """
        # t_i = hash_fun(s_i||0||l_i)
        return hash_fun(self.__s_i, self.l_i, val_opt="0")

    def get_k_i(self):
        """
        Returns the value of the decrypt key (k_i).

        Args:
            N/A

        Returns:
            hex digest (string): hash of s_i + "1" + l_i
        """
        # k_i = hash_fun(s_i||1||l_i)
        return hash_fun(self.__s_i, self.l_i, val_opt="1")


class Edge:
    def __init__(self, t_i, l_j, t_j, k_j):
        """
        Constructor for edge. Given the parent derive key, child label, child
        derive key and child decrypt key the edge will calculate the edge seed
        and the edge label.

        Args:
            t_i (string): hex string of parent derive key
            l_j (string): hex string of child label
            t_j (string): hex string of child dervive key
            k_j (string): hex string of child decrypt key

        Returns:
            N/A
        """
        # r_ij = hash_fun(t_i||l_j)
        self.__r_ij = hash_fun(t_i, l_j)
        # y_ij = AES.encrypt{r_ij}(t_j||k_j)
        self.y_ij = encrypt(self.__r_ij, t_j, k_j)

    def update_r_ij(self, t_i, l_j):
        self.r_ij = hash_fun(t_i, l_j)

    def update_y_ij(self, t_j, k_j):
        self.y_ij = encrypt(self.__r_ij, t_j, k_j)


class DAG:
    def __init__(self, input_matrix, node_names, node_user_map):
        """
        Constructor for DAG. Takes in adjacency list matrix input from main.py

        Args:
            input_matrix (list): list contains another list of zeros and ones
                                 that define edges between nodes

        Returns:
            N/A
        """
        self.node_list = {}

        for node_name in node_names:
            self.add_node(node_name, node_user_map[node_name])

        for i in range(len(input_matrix)):
            for j in range(len(input_matrix[i])):
                if(input_matrix[i][j] == 1):
                    self.add_edge(node_names[i], node_names[j])

    def add_node(self, name, users):
        """
        Adds a Node object to the node_list dictionary on the DAG.

        Args:
            name (string): key to be used for node in node_list

        Returns:
            N/A
        """
        if name not in self.node_list.keys():
            self.node_list[name] = Node(name, users)

    def add_edge(self, paren_node, child_node):
        """
        Given a the name of a parent and child node, an edge will be created
        between them.

        Args:
            paren_node (string): name identifying parent node
            child_node (string): name identifying child node

        Returns:
            N/A
        """
        if(paren_node == child_node):
            return False

        paren = self.node_list[paren_node]
        child = self.node_list[child_node]

        if child_node in paren.edges:
            return False

        new_edge = Edge(
            paren.get_t_i(), child.l_i, child.get_t_i(), child.get_k_i())

        self.node_list[paren_node].edges[child_node] = new_edge

        if not self.is_cyclic():
            return True
        else:
            self.node_list[paren_node].edges.pop(child_node)
            return False
    
    def have_path(self, src_node, des_node):
        """
        Checks to see if there is a path between two nodes.

        Args:
            src_node (string): name to identify starting node
            des_node (string): name to identify target destination node

        Returns:
            boolean: True or False depending on if there is a valid path
        """
        visited = set()
        queue = []
        # visit the first node and place on queue
        visited.add(src_node)
        queue.append(src_node)

        while queue:
            # grab node from front of queue
            popped_node = queue.pop(0)

            if popped_node == des_node:
                return True

            for adj_node in self.node_list[popped_node].edges:
                if adj_node not in visited:
                    queue.append(adj_node)
                    visited.add(adj_node)

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
            if (node not in desc) and (self.have_path(v_i, node)):
                desc.append(node)
        return desc

    def predecessor(self, v_i):
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
            if (node not in pred) and (v_i in self.node_list[node].edges):
                pred.append(node)
        return pred

    def is_cyclic_util(self, node, visited, rec_stack):
        """
        Method to help is_cyclic determine if a graph is cyclic.

        Args:
            node (string): key to identify a node in the graph
            visited (dictionary): keeps track of previously visited nodes
            rec_stack (dictionary): used for recursion

        Returns:
            boolean: True if graph is cyclic

        """
        # Mark current node as visited and adds to recursion stack
        visited[node] = True
        rec_stack[node] = True

        # Recur for all neighbours if any neighbour is visited
        # and in recStack then graph is cyclic
        for children in self.node_list[node].edges.keys():
            if visited[children] is False:
                if self.is_cyclic_util(children, visited, rec_stack):
                    return True
            elif rec_stack[children]:
                return True

        # The node needs to be poped from
        # recursion stack before function ends
        rec_stack[node] = False
        return False

    def is_cyclic(self):
        """
        Returns True if graph is cyclic else False

        Args:
            N/A

        Returns:
            boolean: True if graph is cyclic

        """
        visited = dict()
        recStack = dict()
        for node in self.node_list.keys():
            visited[node] = False
        rec_stack = visited.copy()
        for node in self.node_list.keys():
            if visited[node] is False:
                if self.is_cyclic_util(node, visited, rec_stack):
                    return True
        return False

    def update_label(self, node):
        """
        Changes the label of a node to a new random value

        Args:
            node (string): key to identify node in graph

        Returns:
            N/A

        """
        self.node_list[node].l_i = hashlib.md5(os.urandom(16)).hexdigest()

    def del_edge(self, parent_node, child_node):
        """
            Given two nodes this method will remove the edge between them.
            First generates a new label (ID) for the parent and recomputes
            new k. Then the label is updated for all descendants of the
            parent role. Then for all the roles involved find the predecessors
            and update their edge keys.

        Args:
            parent_node (string): key to identify parent node in graph
            child_node (string): key to idenfity child node in graph

        Returns:
            N/A

        """
        # generate a new ID for parent and compute new k
        # update publicID for all the decs of role
        # for all the roles involved, find the pred sets and update edge keys
        for node in self.descendant(child_node):
            self.update_label(node)

        for node in self.descendant(child_node):
            for pred in self.predecessor(node):
                self.node_list[pred].edges[node].update_r_ij(
                    self.node_list[pred].get_t_i(), self.node_list[node].l_i)
                self.node_list[pred].edges[node].update_y_ij(
                    self.node_list[node].get_t_i(),
                    self.node_list[node].get_k_i())

        self.node_list[parent_node].edges.pop(child_node)

    def del_role(self, node):
        """
        Deletes a node and it's edges from the graph.

        Args:
            node (string): key to identify node in graph

        Returns:
            N/A

        """
        for node_name, node_obj in self.node_list.items():
            if node_name == node:
                # del all children edges
                for children in list(node_obj.edges):
                    self.del_edge(node_name, children)
            if node in node_obj.edges:
                # del all parent edges
                self.del_edge(node_name, node)
        self.node_list.pop(node)

    def update_node_secret(self, node):
        """
        Update the secret key for a node and then compute the new private key.
        Also update edge keys to reflect this change.

        Args:
            node (string): key to identify node in graph

        Returns:
            N/A

        """
        # update the secret key first, then compute
        # the new private key for the role
        self.node_list[node].update_secret()

        for pred in self.predecessor(node):
            self.node_list[pred].edges[node].update_r_ij(
                self.node_list[pred].get_t_i(), self.node_list[node].l_i)
            self.node_list[pred].edges[node].update_y_ij(
                self.node_list[node].get_t_i(), self.node_list[node].get_k_i())

        # for edges from this role, change edge keys
        for children in self.node_list[node].edges.keys():
            self.node_list[node].edges[children].update_r_ij(
                self.node_list[node].get_k_i(), self.node_list[children].l_i)
            self.node_list[node].edges[children].update_y_ij(
                self.node_list[children].get_t_i(),
                self.node_list[children].get_k_i())


    def remove_node_user(self, node, username):
        idx = -1
        for i, user in enumerate(self.node_list[node].users):
            if user.username == username:
                idx = i
        if idx > -1:
            self.node_list[node].users.pop(idx)
        self.update_node_secret(node)


    def add_node_user(self, node, user):
        self.node_list[node].users.append(user)
        self.update_node_secret(node)


    def get_path(self, src_node, des_node, cur_path):
        cur_path.append(src_node)
        if src_node == des_node:
            return cur_path

        for children in self.node_list[src_node].edges.keys():
            path = self.get_path(children, des_node, cur_path)
            if len(path) > 0:
                return path
        return []

    #derive kays alone the path from get_path()
    def derive_key(self, path):
        src_node = path[0]
        t_j = self.node_list[src_node].get_t_i()
        k_j = "something"
        for i in range(1, len(path)):
            child = path[i]
            t_j, k_j = decrypt(hash_fun(t_j, self.node_list[child].l_i), self.node_list[src_node].edges[child].y_ij)
            src_node = child
        return k_j

    ## derive keys when checking the path
    # def derive_key(self, src_node, des_node, t_i, k_i="something"):
    #     if src_node == des_node:
    #         return k_i
    #     for children in self.node_list[src_node].edges.keys():
    #         t_j, k_j = decrypt(hash_fun(t_i, self.node_list[children].l_i), self.node_list[src_node].edges[children].y_ij)
    #         k_j = self.derive_key(children, des_node, t_i)
    #         if k_j not "something":
    #             return k_j
    #     return "something"            
    
    def derive_desc_key(self, src_node, t_i):
        key_list = []
        for children in self.node_list[src_node].edges.keys():
            t_j, k_j = decrypt(hash_fun(t_i, self.node_list[children].l_i), self.node_list[src_node].edges[children].y_ij)
            key_list.append(k_j)
            key_list = key_list + self.derive_desc_key(children, t_j)
        return key_list


    def get_pub(self):
        nodes = []
        edges = []
        for node, node_obj in self.node_list.items():
            nodes.append([node, node_obj.l_i])
            for edge, edge_obj in self.node_list[node].edges.items():
                edges.append([node, edge, edge_obj.y_ij])
        return [nodes, edges]
        
        # pub = dict()
        # for node, node_obj in self.node_list.items():
        #     cur_node = dict()
        #     pub[node] = cur_node
        #     cur_node["label"] = node_obj.l_i
        #     cur_edges = dict()
        #     cur_node["edges"] = cur_edges
        #     for edge, edge_obj in self.node_list[node].edge.items():
        #         cur_edges[edge] = edge_obj.y_ij
        # return pub


    '''
    def rev_user(self, access_list):
        """
        Doesn't handle user level operations. Updates keys and labels at
        a node level. Should be called in ACP part with the list of names
        of nodes the user can access

        Args:
            access_list (list): list of node names that user can access

        Returns:
            N/A
        """
        desc = []
        for node in access_list:
            for des_node in self.descendant(node):
                if des_node not in desc:
                    desc.append(des_node)

        for node in desc:
            self.update_label(node)
        for node in desc:
            for pred in self.predecessor(node):
                self.node_list[pred].edges[node].update_r_ij(
                    self.node_list[pred].get_t_i(), self.node_list[node].l_i)
                self.node_list[pred].edges[node].update_y_ij(
                    self.node_list[node].get_t_i(),
                    self.node_list[node].get_k_i())
    '''

# def ancestory(v_i, graph):
#     """
#     Find all v_j s.t. there is a path from v_j to v_i.

#     Args:
#         v_i (Node): Node to find ancestors of.
#         graph (np.ndarray): Adjacency matrix of DAG.

#     Returns:
#         v_j (list): List of ancestor nodes of v_i.
#     """

#     return v_j


# def successor(v_i, graph):
#     """
#     Find all v_j s.t. there is a directed edge connecting v_i to v_j.

#     Args:
#         v_i (Node): Node to find successors of.
#         graph (np.ndarray): Adjacency matrix of DAG.

#     Returns:
#         v_j (list): List of successor nodes of v_i.
#     """

#     return v_j
