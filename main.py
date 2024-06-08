import os
import osmnx as ox
import networkx as nx
import numpy as np
from tqdm import tqdm
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

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
        if os.path.exists(quartiers[i] + ".graphml"):
            print("Chargement du graphe " + quartiers[i] + " depuis le fichier...")
            self.quartier = ox.load_graphml(quartiers[i] + ".graphml")
        else:
            print("Téléchargement du graphe " + quartiers[i] + "...")
            self.quartier = ox.graph_from_place(quartiers[i], network_type='drive')
            ox.save_graphml(self.quartier, quartiers[i] + ".graphml")
        return self.graph

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
        self.quartier = []
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

def main():
    city_name = 'Montreal, Quebec, Canada'
    file_path = 'montreal.graphml'

    # Charger le graphe
    manager = GraphManager(city_name, file_path)
    
    # Test avec un quartier

    #graph_quartier = manager.get_graph_district(1)

    # Test avec Montréal
    graph_quartier = manager.load_or_download_graph()
    
    # Résoudre le problème du postier chinois
    postman_path_quartier, postman_distance_quartier = manager.solve_chinese_postman(graph_quartier)
    print("Chemin du postier chinois :", postman_path_quartier)
    print("Distance totale pour le chemin du postier chinois :", postman_distance_quartier)

if __name__ == "__main__":
    main()
