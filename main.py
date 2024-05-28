import os
import osmnx as ox
import networkx as nx

class GraphDownloader:
    def __init__(self, city_name):
        self.city_name = city_name

    def download_graph(self, network_type='drive'):
        self.graph = ox.graph_from_place(self.city_name, network_type=network_type)
        return self.graph

    def save_graph(self, file_path):
        ox.save_graphml(self.graph, file_path)


class GraphHandler:
    def __init__(self, file_path):
        self.graph = ox.load_graphml(file_path)
    
    def get_graph_info(self):
        return nx.info(self.graph)
    
    def find_shortest_path(self, origin, destination):
        origin_node = ox.distance.nearest_nodes(self.graph, X=origin[1], Y=origin[0])
        destination_node = ox.distance.nearest_nodes(self.graph, X=destination[1], Y=destination[0])
        return nx.shortest_path(self.graph, origin_node, destination_node, weight='length')


class PathOptimizer:
    def __init__(self, graph_handler):
        self.graph = graph_handler.graph

    def optimize_drone_path(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return list(self.graph.nodes)

    def optimize_snow_removal_path(self, identified_areas):
        """_summary_

        Args:
            identified_areas (_type_): _description_

        Returns:
            _type_: _description_
        """
        return identified_areas


def main():
    city_name = "Montréal, Québec, Canada"
    graph_file = "montreal_graph.graphml"

    if not os.path.exists(graph_file):
        downloader = GraphDownloader(city_name)
        graph = downloader.download_graph()
        downloader.save_graph(graph_file)

    handler = GraphHandler(graph_file)
    print(handler.get_graph_info())

    optimizer = PathOptimizer(handler)
    drone_path = optimizer.optimize_drone_path()
    print("Drone path:", drone_path)

    identified_areas = list(handler.graph.nodes)[:10]
    snow_removal_path = optimizer.optimize_snow_removal_path(identified_areas)
    print("Snow removal path:", snow_removal_path)

if __name__ == "__main__":
    main()
