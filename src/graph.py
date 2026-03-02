<<<<<<< HEAD
class Graph:
    def __init__(self):
        self.graph = {}

    def add_node(self, node):
        if node not in self.graph:
            self.graph[node] = []

    def add_edge(self, from_node, to_node, weight):
        if from_node not in self.graph:
            self.add_node(from_node)
        if to_node not in self.graph:
            self.add_node(to_node)

        self.graph[from_node].append((to_node, weight))

    def update_traffic(self, from_node, to_node, new_weight):
        """Dynamically update road weight (traffic simulation)"""
        for i, (neighbor, weight) in enumerate(self.graph[from_node]):
            if neighbor == to_node:
                self.graph[from_node][i] = (to_node, new_weight)
                break

    def get_nodes(self):
        return list(self.graph.keys())

    def get_neighbors(self, node):
        return self.graph.get(node, [])
=======

>>>>>>> a37d40f0a48661abc9c486297e1c5862c58273c2
