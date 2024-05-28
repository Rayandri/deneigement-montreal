import os
import osmnx as ox
import networkx as nx
import numpy as np

class GraphManager:
    """Class to manage downloading and loading the graph."""
    
    def __init__(self, city_name, file_path):
        self.city_name = city_name
        self.file_path = file_path
        self.graph = None
    
    def load_or_download_graph(self):
        """Load the graph from file if it exists, otherwise download it."""
        if os.path.exists(self.file_path):
            self.graph = ox.load_graphml(self.file_path)
        else:
            self.graph = ox.graph_from_place(self.city_name, network_type='drive')
            ox.save_graphml(self.graph, self.file_path)
        return self.graph
    
    def get_graph_info(self):
        """Return basic information about the graph."""
        return nx.info(self.graph)


class GraphEulirizer:
    """Class to eulerize the graph."""
    
    def __init__(self, graph):
        self.graph = graph
    
    def eulerize_graph(self):
        """Convert the graph into an Eulerian graph."""
        # Placeholder for Eulerian path creation
        # Implementation would involve making the graph Eulerian
        eulerized_graph = nx.eulerize(self.graph)
        return eulerized_graph


class GraphSegmenter:
    """Class to segment the graph by neighborhoods."""
    
    def __init__(self, graph):
        self.graph = graph
    
    def segment_by_neighborhood(self, neighborhoods):
        """Segment the graph into subgraphs based on neighborhoods."""
        subgraphs = {}
        for name, bbox in neighborhoods.items():
            nodes = ox.graph_from_bbox(bbox['north'], bbox['south'], bbox['east'], bbox['west'], network_type='drive').nodes
            subgraphs[name] = self.graph.subgraph(nodes)
        return subgraphs


def main():
    city_name = "Montréal, Québec, Canada"
    graph_file = "montreal_graph.graphml"
    
    manager = GraphManager(city_name, graph_file)
    graph = manager.load_or_download_graph()
    print(manager.get_graph_info())
    
    eulirizer = GraphEulirizer(graph)
    eulerized_graph = eulirizer.eulerize_graph()
    
    neighborhoods = {
        "Outremont": {"north": 45.520, "south": 45.510, "east": -73.590, "west": -73.610},
        "Verdun": {"north": 45.470, "south": 45.450, "east": -73.560, "west": -73.600},
    }
    
    segmenter = GraphSegmenter(graph)
    subgraphs = segmenter.segment_by_neighborhood(neighborhoods)
    
    for name, subgraph in subgraphs.items():
        print(f"Neighborhood: {name}")
        print(nx.info(subgraph))


if __name__ == "__main__":
    main()
