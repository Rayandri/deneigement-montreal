import os
import sys
from contextlib import contextmanager
import osmnx as ox
import networkx as nx
from colorama import Fore, Style, init

# Initialiser colorama
init()


@contextmanager
def suppress_output():
    """Redirige temporairement stdout et stderr vers /dev/null pour supprimer les sorties."""
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    try:
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
        yield
    finally:
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = original_stdout
        sys.stderr = original_stderr


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
            self.graph = ox.graph_from_place(
                self.city_name, network_type='drive')
            ox.save_graphml(self.graph, self.file_path)
        return self.graph

    def get_graph_district(self, i, quartiers):
        """
        Charger le graphe à partir du fichier si disponible, sinon le télécharger.

        :return: Le graphe de la ville.
        """
        # On va tous mettre dans le dossier graph
        if not os.path.exists("graph"):
            os.mkdir("graph")
        os.chdir("graph")
        self.quartier = []
        if os.path.exists(self.file_path):
            print("Chargement du graphe " +
                  quartiers[i] + " depuis le fichier...")
            self.quartier = ox.load_graphml(quartiers[i] + ".graphml")
        else:
            print("Téléchargement du graphe " + quartiers[i] + "...")
            self.quartier = ox.graph_from_place(
                quartiers[i], network_type='drive')
            ox.save_graphml(self.quartier, quartiers[i] + ".graphml")
        os.chdir("..")
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
            odd_degree_nodes = [
                node for node, degree in undirected_graph.degree() if degree % 2 == 1]
            for i in range(0, len(odd_degree_nodes), 2):
                undirected_graph.add_edge(
                    odd_degree_nodes[i], odd_degree_nodes[i + 1], length=0)

        # Vérifier et assigner l'attribut 'length' pour toutes les arêtes
        for u, v, data in undirected_graph.edges(data=True):
            if 'length' not in data:
                try:
                    data['length'] = nx.shortest_path_length(
                        graph, u, v, weight='length')
                except nx.NetworkXNoPath:
                    # Assign default length if no path is found
                    data['length'] = 1
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
            total_distance += eulerized_graph[u][v].get('length', 1)  # Default length of 1 if not found
        circuit.append(circuit[0])  # Retourner au point de départ
        return circuit, total_distance



def optimize_drone_path(graph):
    """
    Optimiser le trajet du drone en utilisant le problème du postier chinois.

    :param graph: Le graphe pour lequel optimiser le trajet.
    :return: Le chemin optimisé et la distance totale.
    """
    undirected_graph = graph.to_undirected()
    eulerized_graph = nx.eulerize(undirected_graph)
    
    # Vérifier et assigner l'attribut 'length' pour toutes les arêtes
    for u, v, data in eulerized_graph.edges(data=True):
        if 'length' not in data:
            try:
                data['length'] = nx.shortest_path_length(graph, u, v, weight='length')
            except nx.NetworkXNoPath:
                data['length'] = 1  # Assign default length if no path is found
    
    eulerian_circuit = list(nx.eulerian_circuit(eulerized_graph, source=list(eulerized_graph.nodes())[0]))
    drone_path = []
    total_distance = 0
    for u, v in eulerian_circuit:
        drone_path.append(u)
        total_distance += eulerized_graph[u][v].get('length', 1)  # Default length of 1 if not found
    drone_path.append(drone_path[0])  # Retourner au point de départ
    return drone_path, total_distance



def main():
    city_name = 'Montreal, Quebec, Canada'
    file_path = 'montreal.graphml'

    # Charger le graphe de la ville
    manager = GraphManager(city_name, file_path)

    quartiers = ["Outremont, Montreal, Canada", "Verdun, Montreal, Canada", "Anjou, Montreal, Canada",
                 "Rivière-des-Prairies-Pointe-aux-Trembles, Montreal, Canada", "Le Plateau-Mont-Royal, Montreal, Canada"]

    results = []

    for i, quartier in enumerate(quartiers):
        quartier_results = {"quartier": quartier}

        # Charger le graphe du quartier
        graph_quartier = manager.get_graph_district(i, quartiers)

        with suppress_output():
            # Optimiser le trajet du drone (Problème 1)
            drone_path_quartier, distance_quartier = optimize_drone_path(
                graph_quartier)
            quartier_results["drone_path"] = drone_path_quartier
            quartier_results["drone_distance"] = distance_quartier

            # Identifier les zones nécessitant un déneigement
            snow_removal_nodes_quartier = drone_path_quartier

            # Résoudre le problème du postier chinois (Problème 2)
            postman_path_quartier, postman_distance_quartier = manager.solve_chinese_postman(
                graph_quartier)
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
        break

    # Afficher le résumé final
    print(Fore.CYAN + "\nRésumé des opérations de déneigement pour tous les quartiers :" + Style.RESET_ALL)
    for result in results:
        print(Fore.YELLOW +
              f"\nQuartier : {result['quartier']}" + Style.RESET_ALL)
        print(Fore.MAGENTA +
              f"Distance totale pour le chemin du drone : {result['drone_distance']:.2f} km" + Style.RESET_ALL)
        print(Fore.MAGENTA +
              f"Distance totale pour le chemin du postier chinois : {result['postman_distance']:.2f} km" + Style.RESET_ALL)
        print(
            Fore.BLUE + f"Coût du vol du drone : {result['drone_cost']:.2f} €" + Style.RESET_ALL)
        print(
            Fore.RED + f"Coût des opérations de déneigement avec véhicules type I : {result['vehicle_cost_type_I']:.2f} €" + Style.RESET_ALL)
        print(
            Fore.RED + f"Coût des opérations de déneigement avec véhicules type II : {result['vehicle_cost_type_II']:.2f} €" + Style.RESET_ALL)

    print(Fore.CYAN + "\nOptimisation des trajets de déneigement terminée pour tous les quartiers." + Style.RESET_ALL)


if __name__ == "__main__":
    main()
