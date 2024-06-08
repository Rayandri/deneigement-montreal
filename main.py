import os
import osmnx as ox
import networkx as nx
import numpy as np
from tqdm import tqdm
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from concorde.tsp import TSPSolver
from colorama import Fore, Style, init
import contextlib

# Initialiser colorama
init()

class GraphManager:
    """Classe pour gérer le téléchargement, le chargement, l'eulérisation et l'optimisation des trajets dans un graphe urbain."""

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
        quartiers = [
            "Outremont, Montreal, Canada",
            "Verdun, Montreal, Canada",
            "Anjou, Montreal, Canada",
            "Rivière-des-Prairies-Pointe-aux-Trembles, Montreal, Canada",
            "Le Plateau-Mont-Royal, Montreal, Canada"
        ]
        if not os.path.exists('graph'):
            os.makedirs('graph')
        quartier_file_path = os.path.join('graph', quartiers[i] + ".graphml")
        print("Téléchargement du graphe " + quartiers[i] + "...")
        if os.path.exists(quartier_file_path):
            self.quartier = ox.load_graphml(quartier_file_path)
        else:
            self.quartier = ox.graph_from_place(quartiers[i], network_type='drive')
            ox.save_graphml(self.quartier, quartier_file_path)
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

    def eulerize_graph(self, graph):
        """
        Rendre le graphe eulérien en ajoutant des arêtes.

        :param graph: Le graphe à eulériser.
        :return: Le graphe eulérisé.
        """
        undirected_graph = graph.to_undirected()
        if not nx.is_eulerian(undirected_graph):
            odd_degree_nodes = [node for node, degree in undirected_graph.degree() if degree % 2 == 1]
            for i in range(0, len(odd_degree_nodes), 2):
                undirected_graph.add_edge(odd_degree_nodes[i], odd_degree_nodes[i+1], length=0)
        return undirected_graph

    def solve_chinese_postman(self, graph):
        """
        Résoudre le problème du postier chinois pour optimiser les trajets des véhicules de déneigement.

        :param graph: Le graphe pour lequel résoudre le problème.
        :return: Le circuit optimal et sa longueur.
        """
        eulerized_graph = self.eulerize_graph(graph)
        eulerian_circuit = list(nx.eulerian_circuit(eulerized_graph, source=list(eulerized_graph.nodes())[0]))
        circuit = []
        total_distance = 0
        for u, v in eulerian_circuit:
            circuit.append(u)
            total_distance += eulerized_graph[u][v][0]['length']
        circuit.append(circuit[0])  # Retourner au point de départ
        return circuit, total_distance

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
    with open(os.devnull, 'w') as fnull:
        with contextlib.redirect_stdout(fnull), contextlib.redirect_stderr(fnull):
            solver = TSPSolver.from_data(distance_matrix, norm="GEO", ys=nodes)
            solution = solver.solve()
    drone_path = [nodes[i] for i in solution.tour]
    return drone_path, solution.optimal_value

def main():
    city_name = 'Montreal, Quebec, Canada'
    file_path = os.path.join('graph', 'montreal.graphml')
    
    # Charger le graphe de la ville
    manager = GraphManager(city_name, file_path)
    #graph = manager.load_or_download_graph()
    
    quartiers = ["Outremont, Montreal, Canada", "Verdun, Montreal, Canada", "Anjou, Montreal, Canada",
                 "Rivière-des-Prairies-Pointe-aux-Trembles, Montreal, Canada", "Le Plateau-Mont-Royal, Montreal, Canada"]
    
    results = []
    
    for i, quartier in enumerate(quartiers):
        quartier_results = {"quartier": quartier}
        
        # Charger le graphe du quartier
        
        graph_quartier = manager.get_graph_district(i)
        
        # Optimiser le trajet du drone (Problème 1)
        nodes_quartier, distance_matrix_quartier = create_distance_matrix(graph_quartier)
        drone_path_quartier, distance_quartier = optimize_drone_path(distance_matrix_quartier, nodes_quartier)
        quartier_results["drone_path"] = drone_path_quartier
        quartier_results["drone_distance"] = distance_quartier
        
        # Identifier les zones nécessitant un déneigement
        snow_removal_nodes_quartier = drone_path_quartier
        
        # Résoudre le problème du postier chinois (Problème 2)
        postman_path_quartier, postman_distance_quartier = manager.solve_chinese_postman(graph_quartier)
        quartier_results["postman_path"] = postman_path_quartier
        quartier_results["postman_distance"] = postman_distance_quartier
        
        # Modèle de coût (Problème 3)
        drone_cost = 100 + 0.01 * distance_quartier
        vehicle_cost_type_I = 500 + 1.1 * postman_distance_quartier
        vehicle_cost_type_II = 800 + 1.3 * postman_distance_quartier
        
        quartier_results["drone_cost"] = drone_cost
        quartier_results["vehicle_cost_type_I"] = vehicle_cost_type_I
        quartier_results["vehicle_cost_type_II"] = vehicle_cost_type_II
        
        results.append(quartier_results)
    
    # Afficher le résumé final
    print(Fore.CYAN + "\nRésumé des opérations de déneigement pour tous les quartiers :" + Style.RESET_ALL)
    for result in results:
        print(Fore.YELLOW + f"\nQuartier : {result['quartier']}" + Style.RESET_ALL)
        print(Fore.GREEN + f"Chemin du drone : {result['drone_path']}" + Style.RESET_ALL)
        print(Fore.GREEN + f"Distance totale pour le chemin du drone : {result['drone_distance']:.2f} km" + Style.RESET_ALL)
        print(Fore.MAGENTA + f"Chemin du postier chinois : {result['postman_path']}" + Style.RESET_ALL)
        print(Fore.MAGENTA + f"Distance totale pour le chemin du postier chinois : {result['postman_distance']:.2f} km" + Style.RESET_ALL)
        print(Fore.BLUE + f"Coût du vol du drone : {result['drone_cost']:.2f} €" + Style.RESET_ALL)
        print(Fore.RED + f"Coût des opérations de déneigement avec véhicules type I : {result['vehicle_cost_type_I']:.2f} €" + Style.RESET_ALL)
        print(Fore.RED + f"Coût des opérations de déneigement avec véhicules type II : {result['vehicle_cost_type_II']:.2f} €" + Style.RESET_ALL)
    
    print(Fore.CYAN + "\nOptimisation des trajets de déneigement terminée pour tous les quartiers." + Style.RESET_ALL)

if __name__ == "__main__":
    main()
