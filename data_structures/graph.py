"""
Graph (Adjacency List) Data Structure

Time Complexity:
  - add_node(node): O(1)
  - add_edge(from_node, to_node): O(1)
  - get_neighbors(node): O(1) to retrieve; O(k) to iterate where k = # neighbors
  - get_all_nodes(): O(n) where n = number of nodes
  - DFS/BFS: O(n + e) where n = nodes, e = edges

Space Complexity: O(n + e) where n = nodes, e = edges

Use Case: Model lesson prerequisites and learning paths
"""


class Graph:
    def __init__(self):
        """Initialize an empty graph using adjacency list."""
        self.adjacency_list = {}

    def add_node(self, node):
        """
        Add a node to the graph.
        
        Time: O(1)
        """
        if node not in self.adjacency_list:
            self.adjacency_list[node] = []

    def add_edge(self, from_node, to_node):
        """
        Add a directed edge from from_node to to_node.
        
        Time: O(1)
        Automatically creates nodes if they don't exist.
        """
        self.add_node(from_node)
        self.add_node(to_node)
        if to_node not in self.adjacency_list[from_node]:
            self.adjacency_list[from_node].append(to_node)

    def get_neighbors(self, node):
        """
        Get all neighbors (outgoing edges) of a node.
        
        Time: O(1) to retrieve list; O(k) to iterate where k = # neighbors
        """
        return self.adjacency_list.get(node, [])

    def get_all_nodes(self):
        """
        Get all nodes in the graph.
        
        Time: O(n) where n = number of nodes
        """
        return list(self.adjacency_list.keys())

    def dfs(self, start_node, visited=None):
        """
        Depth-First Search from a starting node.
        
        Time: O(n + e) where n = nodes, e = edges
        Returns list of nodes in DFS order.
        """
        if visited is None:
            visited = set()
        result = []

        def _dfs_helper(node):
            if node in visited:
                return
            visited.add(node)
            result.append(node)
            for neighbor in self.get_neighbors(node):
                _dfs_helper(neighbor)

        _dfs_helper(start_node)
        return result

    def bfs(self, start_node):
        """
        Breadth-First Search from a starting node.
        
        Time: O(n + e) where n = nodes, e = edges
        Returns list of nodes in BFS order.
        """
        from collections import deque
        visited = set()
        queue = deque([start_node])
        result = []

        while queue:
            node = queue.popleft()
            if node in visited:
                continue
            visited.add(node)
            result.append(node)
            for neighbor in self.get_neighbors(node):
                if neighbor not in visited:
                    queue.append(neighbor)

        return result
