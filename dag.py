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
        self.edges = {}
        self.name = name

    def update_s_i(self):
        self.s_i = hashlib.md5(os.urandom(16)).hexdigest()

    def get_t_i(self):
        """
        Returns the value of the derive key (t_i).

        Args:
            N/A

        Returns:
            hex digest (string): hash of __s_i + "0" + l_i
        """
        # t_i = F_s_i(0||l_i)
        return F(self.__s_i, self.l_i, val_opt="0")

    def get_k_i(self):
        """
        Returns the value of the decrypt key (k_i).

        Args:
            N/A

        Returns:
            hex digest (string): hash of __si_i + "1" + l_i
        """
        # k_i = F_s_i(1||l_i)
        return F(self.__s_i, self.l_i, val_opt="1")


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
        # r_ij = F_ti(l_j)
        self.__r_ij = F(t_i, l_j)
        # y_ij = Enc_r_ij(t_j||k_j)
        self.y_ij = Enc(self.__r_ij, t_j, k_j)

    def update_r_ij(self, t_i, l_j):
        self.r_ij = F(t_i, l_j)

    def update_y_ij(self, t_j, k_j):
        self.y_ij = Enc(self.__r_ij, t_j, k_j)


class DAG:
    def __init__(self, input_matrix):
        """
        Constructor for DAG. Takes in adjacency list matrix input from main.py

        Args:
            input_matrix (list): list contains another list of zeros and ones
                                that define edges between nodes

        Returns:
            N/A
        """
        self.node_list = {}
        self.input_matrix = input_matrix

    def add_node(self, name):
        """
        Adds a Node object to the node_list dictionary on the DAG.

        Args:
            name (string): key to be used for node in node_list

        Returns:
            N/A
        """
        self.node_list[name] = Node(name)

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
            # self.del_edge(paren_node, child_node)
            self.node_list[paren_node].edges.pop(child_node)
            return False

    def create_graph(self):
        """
        Uses data stored in input_matrix variable to create a DAG.
        Use the index of input_matrix as the name of the nodes here.

        Args:
            N/A

        Returns:
            N/A
        """
        for i in range(len(self.input_matrix)):
            self.add_node(str(i))

        for i in range(len(self.input_matrix)):
            for j in range(len(self.input_matrix[i])):
                if(self.input_matrix[i][j] == 1):
                    self.add_edge(str(i), str(j))

    def have_path(self, src_node, des_node):
        """
        Checks to see if there is a path between two nodes.

        Args:
            src_node (string): name to identify starting node
            des_node (string): name to identify target destination node

        Returns:
            boolean: True or False depending on if there is a valid path
        """
        # if src_node == des_node:
        #     return True
        # for nodes in self.node_list[src_node].edges.keys():
        #     if self.have_path(nodes, des_node):
        #         return True
        # return False

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
        return False

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
            if (node not in pred) and (node in self.node_list[v_i].edges):
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

        """
        Recur for all neighbours if any neighbour is visited
        and in recStack then graph is cyclic
        """
        for children in self.node_list[node].edges.keys():
            if visited[children] is False:
                if self.is_cyclic_util(children, visited, rec_stack):
                    return True
            elif rec_stack[children]:
                return True
        """
        The node needs to be poped from
        recursion stack before function ends
        """
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
        print(f"parent_node: {parent_node}\nchild_node: {child_node}")

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

    def update_secret_i(self, node):
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
        self.node_list[node].update_s_i()

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
