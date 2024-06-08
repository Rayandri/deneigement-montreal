import os
import osmnx as ox
import networkx as nx
import numpy as np
from tqdm import tqdm
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from concorde.tsp import TSPSolver

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
        self.quartier = None

    def load_or_download_graph(self):
        """
        Charger le graphe à partir du fichier si disponible, sinon le télécharger.

        :return: Le graphe de la ville.
        """
        if os.path.exists(self.file_path):
            print("Chargement du graphe de Montréal depuis le fichier...")
            self.graph = ox.load_graphml(self.file_path)
        else:
            print("Téléchargement du graphe de Montréal...")
            self.graph = ox.graph_from_place(self.city_name, network_type='drive')
            ox.save_graphml(self.graph, self.file_path)
        return self.graph
    
    def get_graph_district(self, i):
        """
        Charger le graphe à partir du fichier si disponible, sinon le télécharger.

        :return: Le graphe de la ville.
        """
        # Initialiser les quartiers
        quartiers = [
            "Outremont, Montreal, Canada",
            "Verdun, Montreal, Canada",
            "Anjou, Montreal, Canada",
            "Rivière-des-Prairies-Pointe-aux-Trembles, Montreal, Canada",
            "Le Plateau-Mont-Royal, Montreal, Canada"
        ]
        self.quartier = []
        # Télécharger et construire le graphe pour chaque quartier
        print("Téléchargement du graphe " + quartiers[i] + "...")
        self.quartier = ox.graph_from_place(quartiers[i], network_type='drive')
        ox.save_graphml(self.quartier, quartiers[i] + ".graphml")
        return self.quartier

    def get_graph_info(self):
        """
        Retourner les informations de base sur le graphe.

        :return: Informations sur le graphe.
        """
        return nx.info(self.graph)

    def get_graph_district_info(self, i):
        """
        Retourner les informations de base sur le graphe.

        :return: Informations sur le graphe.
        """
        return nx.info(self.quartier[i])
    
def create_distance_matrix(graph):
    """
    Créer une matrice de distances à partir d'un graphe.

    :param graph: Le graphe pour lequel créer la matrice de distances.
    :return: Une liste des nœuds et une matrice de distances.
    """
    nodes = list(graph.nodes)
    num_nodes = len(nodes)
    distance_matrix = np.zeros((num_nodes, num_nodes))
    for i, node_i in enumerate(tqdm(nodes, desc="Calcul des distances")):
        for j, node_j in enumerate(nodes):
            if i != j:
                try:
                    distance_matrix[i, j] = nx.shortest_path_length(graph, node_i, node_j, weight='length')
                except nx.NetworkXNoPath:
                    distance_matrix[i, j] = np.inf
    return nodes, distance_matrix

def optimize_drone_path(distance_matrix, nodes):
    """
    Optimiser le trajet du drone en utilisant Concorde TSP Solver.

    :param distance_matrix: Matrice des distances.
    :param nodes: Liste des nœuds.
    :return: Le chemin optimisé et la distance totale.
    """
    solver = TSPSolver.from_data(distance_matrix, norm="GEO", ys=nodes)
    solution = solver.solve()
    drone_path = [nodes[i] for i in solution.tour]
    return drone_path, solution.optimal_value

def create_vrp_graph(graph, snow_removal_nodes):
    """
    Créer un graphe VRP à partir des nœuds nécessitant un déneigement.

    :param graph: Le graphe original.
    :param snow_removal_nodes: Liste des nœuds nécessitant un déneigement.
    :return: Graphe VRP.
    """
    G = nx.DiGraph()
    for u in tqdm(snow_removal_nodes, desc="Création du graphe VRP"):
        for v in snow_removal_nodes:
            if u != v:
                try:
                    cost = nx.shortest_path_length(graph, u, v, weight='length')
                    G.add_edge(u, v, weight=cost)
                except nx.NetworkXNoPath:
                    continue
    return G

def solve_vrp(G, load_capacity, duration):
    """
    Résoudre le problème de routage des véhicules (VRP) en utilisant OR-Tools.

    :param G: Graphe VRP.
    :param load_capacity: Capacité de charge des véhicules.
    :param duration: Durée maximale des trajets.
    :return: Valeur optimale et routes optimisées.
    """
    manager = pywrapcp.RoutingIndexManager(len(G.nodes), 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(G[from_node][to_node]['weight'])

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.seconds = 30

    solution = routing.SolveWithParameters(search_parameters)

    if not solution:
        return None, None

    routes = []
    index = routing.Start(0)
    while not routing.IsEnd(index):
        routes.append(manager.IndexToNode(index))
        index = solution.Value(routing.NextVar(index))
    routes.append(manager.IndexToNode(index))
    
    total_distance = solution.ObjectiveValue()
    
    return total_distance, routes

def main():
    city_name = 'Montreal, Quebec, Canada'
    file_path = 'montreal.graphml'

    # Charger le graphe
    manager = GraphManager(city_name, file_path)
    
    # Test avec un quartier
    graph_quartier = manager.get_graph_district(1)
    # Créer la matrice de distances
    nodes_quartier, distance_matrix_quartier = create_distance_matrix(graph_quartier)
     # Optimiser le trajet du drone
    drone_path_quartier, distance_quartier = optimize_drone_path(distance_matrix_quartier, nodes_quartier)
    print("Chemin du drone :", drone_path_quartier)
    print("Distance totale pour le chemin du drone :", distance_quartier)
    # Identifier les zones nécessitant un déneigement
    snow_removal_nodes_quartier = drone_path_quartier
    # Créer le graphe VRP
    G_quartier = create_vrp_graph(graph_quartier, snow_removal_nodes_quartier)
    # Résoudre le VRP
    best_value_quartier, best_routes_quartier = solve_vrp(G_quartier, load_capacity=10, duration=5)
    print("Valeur optimale pour le VRP :", best_value_quartier)
    print("Routes optimisées pour le VRP :", best_routes_quartier)
    
    
    """
    graph = manager.load_or_download_graph()

    # Créer la matrice de distances
    nodes, distance_matrix = create_distance_matrix(graph)

    # Optimiser le trajet du drone
    drone_path, distance = optimize_drone_path(distance_matrix, nodes)
    print("Chemin du drone :", drone_path)
    print("Distance totale pour le chemin du drone :", distance)

    # Identifier les zones nécessitant un déneigement
    snow_removal_nodes = drone_path

    # Créer le graphe VRP
    G = create_vrp_graph(graph, snow_removal_nodes)

    # Résoudre le VRP
    best_value, best_routes = solve_vrp(G, load_capacity=10, duration=5)
    print("Valeur optimale pour le VRP :", best_value)
    print("Routes optimisées pour le VRP :", best_routes)
    """

if __name__ == "__main__":
    main()
