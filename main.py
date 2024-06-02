import os
import osmnx as ox
import networkx as nx
import numpy as np
from python_tsp.exact import solve_tsp_dynamic_programming
from vrpy import VehicleRoutingProblem
from networkx import DiGraph

class GraphManager:
    """Classe pour gérer le téléchargement et le chargement du graphe de la ville."""

    def __init__(self, city_name, file_path):
        """
        Initialiser le gestionnaire de graphe.

        :param city_name: Nom de la ville pour télécharger le graphe.
        :param file_path: Chemin du fichier pour sauvegarder ou charger le graphe.
        """
        self.city_name = city_name
        self.file_path = file_path
        self.graph = None

    def load_or_download_graph(self):
        """
        Charger le graphe à partir du fichier si disponible, sinon le télécharger.

        :return: Le graphe de la ville.
        """
        if os.path.exists(self.file_path):
            self.graph = ox.load_graphml(self.file_path)
        else:
            self.graph = ox.graph_from_place(self.city_name, network_type='drive')
            ox.save_graphml(self.graph, self.file_path)
        return self.graph

    def get_graph_info(self):
        """
        Retourner les informations de base sur le graphe.

        :return: Informations sur le graphe.
        """
        return nx.info(self.graph)

def create_distance_matrix(graph):
    """
    Créer une matrice de distances à partir d'un graphe.

    :param graph: Le graphe pour lequel créer la matrice de distances.
    :return: Une liste des nœuds et une matrice de distances.
    """
    nodes = list(graph.nodes)
    num_nodes = len(nodes)
    distance_matrix = np.zeros((num_nodes, num_nodes))
    for i, node_i in enumerate(nodes):
        for j, node_j in enumerate(nodes):
            if i != j:
                try:
                    distance_matrix[i, j] = nx.shortest_path_length(graph, node_i, node_j, weight='length')
                except nx.NetworkXNoPath:
                    distance_matrix[i, j] = np.inf
    return nodes, distance_matrix

def optimize_drone_path(distance_matrix, nodes):
    """
    Optimiser le trajet du drone en utilisant TSP.

    :param distance_matrix: Matrice des distances.
    :param nodes: Liste des nœuds.
    :return: Le chemin optimisé et la distance totale.
    """
    permutation, distance = solve_tsp_dynamic_programming(distance_matrix)
    drone_path = [nodes[i] for i in permutation]
    return drone_path, distance

def create_vrp_graph(graph, snow_removal_nodes):
    """
    Créer un graphe VRP à partir des nœuds nécessitant un déneigement.

    :param graph: Le graphe original.
    :param snow_removal_nodes: Liste des nœuds nécessitant un déneigement.
    :return: Graphe VRP.
    """
    G = DiGraph()
    for u in snow_removal_nodes:
        for v in snow_removal_nodes:
            if u != v:
                try:
                    cost = nx.shortest_path_length(graph, u, v, weight='length')
                    G.add_edge(u, v, cost=cost)
                except nx.NetworkXNoPath:
                    continue
    return G

def solve_vrp(G, load_capacity, duration):
    """
    Résoudre le problème de routage des véhicules (VRP).

    :param G: Graphe VRP.
    :param load_capacity: Capacité de charge des véhicules.
    :param duration: Durée maximale des trajets.
    :return: Valeur optimale et routes optimisées.
    """
    prob = VehicleRoutingProblem(G, load_capacity=load_capacity, duration=duration)
    prob.solve()
    return prob.best_value, prob.best_routes

def main():
    city_name = 'Montreal, Quebec, Canada'
    file_path = 'montreal.graphml'

    # Charger le graphe
    manager = GraphManager(city_name, file_path)
    graph = manager.load_or_download_graph()

    # Créer la matrice de distances
    nodes, distance_matrix = create_distance_matrix(graph)

    drone_path, distance = optimize_drone_path(distance_matrix, nodes)
    print("Chemin du drone :", drone_path)
    print("Distance totale pour le chemin du drone :", distance)

    snow_removal_nodes = drone_path

    G = create_vrp_graph(graph, snow_removal_nodes)

    best_value, best_routes = solve_vrp(G, load_capacity=10, duration=5)
    print("Valeur optimale pour le VRP :", best_value)
    print("Routes optimisées pour le VRP :", best_routes)

if __name__ == "__main__":
    main()
