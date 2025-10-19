# file: graph_manager.py

import networkx as nx
import pandas as pd
import json
from networkx.readwrite import json_graph

class GraphManager:
    """A class to manage the NetworkX graph operations."""

    def __init__(self):
        """Initializes an empty graph."""
        self.graph = nx.Graph()

    def load_graph_from_db(self, db_manager):
        """Builds the graph using data fetched from the database."""
        self.graph.clear()
        
        # Add nodes with position attributes for plotting
        locations = db_manager.get_all_locations()
        for name, x, y in locations:
            self.graph.add_node(name, pos=(x, y))
            
        # Add edges with weight attributes
        roads = db_manager.get_all_roads()
        for start, end, weight in roads:
            self.graph.add_edge(start, end, weight=weight)
            
    def find_shortest_path(self, start_node: str, end_node: str) -> list | None:
        """Finds the shortest path using Dijkstra's algorithm."""
        try:
            path = nx.dijkstra_path(self.graph, source=start_node, target=end_node, weight='weight')
            return path
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def get_adjacency_matrix(self) -> tuple[pd.DataFrame, list]:
        """Returns the adjacency matrix as a pandas DataFrame."""
        nodes = list(self.graph.nodes)
        adj_matrix = nx.to_pandas_adjacency(self.graph, nodelist=nodes, weight='weight')
        return adj_matrix, nodes

    def get_incidence_matrix(self) -> tuple[pd.DataFrame, list, list]:
        """Returns the incidence matrix as a pandas DataFrame."""
        nodes = list(self.graph.nodes)
        edges = list(self.graph.edges)
        inc_matrix_sparse = nx.incidence_matrix(self.graph, nodelist=nodes, edgelist=edges, oriented=True)
        inc_df = pd.DataFrame(inc_matrix_sparse.toarray(), index=nodes, columns=[str(e) for e in edges])
        return inc_df, nodes, edges

    def get_node_names(self) -> list:
        """Returns a sorted list of node names."""
        return sorted(list(self.graph.nodes))

    def export_to_json(self, filename='graph_data.json'):
        """Exports the graph data to a JSON file."""
        data = json_graph.node_link_data(self.graph)
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

    def export_to_csv(self, node_file='nodes.csv', edge_file='edges.csv'):
        """Exports nodes and edges to separate CSV files."""
        # Nodes with positions
        nodes_data = {
            'name': [n for n in self.graph.nodes],
            'x': [self.graph.nodes[n]['pos'][0] for n in self.graph.nodes],
            'y': [self.graph.nodes[n]['pos'][1] for n in self.graph.nodes]
        }
        pd.DataFrame(nodes_data).to_csv(node_file, index=False)
        
        # Edges with weights
        nx.to_pandas_edgelist(self.graph).to_csv(edge_file, index=False)