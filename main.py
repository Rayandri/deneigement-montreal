import os
import sys
from contextlib import contextmanager
import osmnx as ox
import networkx as nx
from colorama import Fore, Style, init

import plotly.graph_objects as go

import community as community_louvain


VEHICLE_SPEED_TYPE_I = 10  # km/h
VEHICLE_SPEED_TYPE_II = 20  # km/h
num_vehicles = 3  # Nombre de véhicules disponibles


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


class GraphVisualizerPlotly:
    def __init__(self, graph):
        self.graph = graph
        self.pos = {node: (data['x'], data['y'])
                    for node, data in graph.nodes(data=True)}

    def path_to_edges(self, path):
        """Convertit un chemin de nœuds en une liste d'arêtes."""
        return [(path[i], path[i + 1]) for i in range(len(path) - 1)]

    def animate_graph(self, paths, title, file_name=None):
        """
        Animer le graphe et les chemins optimisés.

        :param paths: Les chemins optimisés à animer (liste de listes d'arêtes).
        :param title: Le titre de l'animation.
        :param file_name: Nom du fichier pour sauvegarder l'animation (si fourni).
        """
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown']

        fig = go.Figure()

        for path_index, path in enumerate(paths):
            edge_x = []
            edge_y = []
            color = colors[path_index % len(colors)]
            for edge in path:
                x0, y0 = self.pos[edge[0]]
                x1, y1 = self.pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

            fig.add_trace(go.Scattermapbox(
                lat=edge_y,
                lon=edge_x,
                mode='lines',
                line=dict(color=color),
                name=f"Déneigeuse {path_index + 1}"
            ))

        node_x = [self.pos[node][0] for node in self.graph.nodes()]
        node_y = [self.pos[node][1] for node in self.graph.nodes()]

        fig.add_trace(go.Scattermapbox(
            lat=node_y,
            lon=node_x,
            mode='markers',
            marker=dict(size=5),
            name='Noeuds'
        ))

        fig.update_layout(
            title=title,
            mapbox_style="open-street-map",
            mapbox=dict(
                center=dict(lat=sum(node_y)/len(node_y),
                            lon=sum(node_x)/len(node_x)),
                zoom=12,
            ),
            updatemenus=[dict(type='buttons', showactive=False,
                            buttons=[dict(label='Play',
                                            method='animate',
                                            args=[None, dict(frame=dict(duration=500, redraw=True), fromcurrent=True)])])],
            showlegend=True
        )

        frames = []
        for i in range(max(len(path) for path in paths)):
            frame_data = []
            for path_index, path in enumerate(paths):
                frame_x = []
                frame_y = []
                color = colors[path_index % len(colors)]
                for edge in path[:i+1]:
                    x0, y0 = self.pos[edge[0]]
                    x1, y1 = self.pos[edge[1]]
                    frame_x.extend([x0, x1, None])
                    frame_y.extend([y0, y1, None])
                frame_data.append(go.Scattermapbox(
                    lat=frame_y, lon=frame_x, mode='lines', line=dict(color=color)))
            frames.append(go.Frame(data=frame_data))

        fig.frames = frames

        if file_name:
            if not os.path.exists("animations"):
                os.makedirs("animations")
            fig.write_html(f"animations/{file_name}")
            
        #fig.show()

    def visualize_results(self, drone_path, circuits, base_file_name):
        """
        Visualiser les résultats pour le chemin du drone et les chemins des déneigeuses.

        :param drone_path: Le chemin optimisé pour le drone.
        :param circuits: Les chemins optimisés pour les déneigeuses.
        :param base_file_name: Base du nom de fichier pour sauvegarder les animations.
        """
        self.animate_graph(circuits, "Chemin optimisé pour les déneigeuses",
                        file_name=f"{base_file_name}_deneigeuses.html")


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

        je crée des routes entre les noeuds de degré impair pour les rendre pair
        sauf que sur lors du parcours je prend le chemin le plus court qui mene de u à v avec des vrai routes existante 

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

    def solve_chinese_postman(self, graph, num_vehicles):
        """
        Résoudre le problème du postier chinois pour optimiser les trajets des véhicules de déneigement.

        :param graph: Le graphe pour lequel résoudre le problème.
        :param num_vehicles: Le nombre de véhicules disponibles.
        :return: Le circuit optimal pour chaque véhicule, la longueur totale et le temps de déneigement.
        """
        eulerized_graph = self.eulerize_graph(graph)
        eulerian_circuit = list(nx.eulerian_circuit(
            eulerized_graph, source=list(eulerized_graph.nodes())[0]))

        total_distance = sum(eulerized_graph[u][v].get(
            'length', 1) for u, v in eulerian_circuit)
        segment_length = total_distance / num_vehicles

        circuits = [[] for _ in range(num_vehicles)]
        vehicle_distances = [0] * num_vehicles
        current_vehicle = 0
        current_distance = 0

        for u, v in eulerian_circuit:
            length = eulerized_graph[u][v].get('length', 1)
            if current_distance + length > segment_length and current_vehicle < num_vehicles - 1:
                current_vehicle += 1
                current_distance = 0
            circuits[current_vehicle].append((u, v))
            vehicle_distances[current_vehicle] += length
            current_distance += length

        # Calculer le temps de déneigement pour chaque véhicule
        times_type_I = [distance /
                        VEHICLE_SPEED_TYPE_I for distance in vehicle_distances]
        times_type_II = [
            distance / VEHICLE_SPEED_TYPE_II for distance in vehicle_distances]

        max_time_type_I = max(times_type_I)
        max_time_type_II = max(times_type_II)

        return circuits, total_distance, max_time_type_I, max_time_type_II


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
                data['length'] = nx.shortest_path_length(
                    graph, u, v, weight='length')
            except nx.NetworkXNoPath:
                data['length'] = 1  # Assign default length if no path is found

    eulerian_circuit = list(nx.eulerian_circuit(
        eulerized_graph, source=list(eulerized_graph.nodes())[0]))
    drone_path = []
    total_distance = 0
    for u, v in eulerian_circuit:
        drone_path.append(u)
        # Default length of 1 if not found
        total_distance += eulerized_graph[u][v].get('length', 1)
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
    cpt = 0

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
            circuits, postman_distance_quartier, max_time_type_I, max_time_type_II = manager.solve_chinese_postman(
                graph_quartier, num_vehicles)
            quartier_results["postman_path"] = circuits
            quartier_results["postman_distance"] = postman_distance_quartier
            quartier_results["time_type_I"] = max_time_type_I
            quartier_results["time_type_II"] = max_time_type_II

            # Modèle de coût (Problème 3)
            drone_cost = 100 + 0.01 * distance_quartier

            # Calcul du coût horaire
            cost_hour_type_I = (min(max_time_type_I, 8) * 1.1 +
                                max(0, max_time_type_I - 8) * 1.3) * num_vehicles
            cost_hour_type_II = (min(max_time_type_II, 8) * 1.3 +
                                max(0, max_time_type_II - 8) * 1.5) * num_vehicles

            # Coût des opérations de déneigement avec véhicules type I
            vehicle_cost_type_I = 500 + 1.1 * postman_distance_quartier + cost_hour_type_I

            # Coût des opérations de déneigement avec véhicules type II
            vehicle_cost_type_II = 800 + 1.3 * postman_distance_quartier + cost_hour_type_II

            quartier_results["drone_cost"] = drone_cost
            quartier_results["vehicle_cost_type_I"] = vehicle_cost_type_I
            quartier_results["vehicle_cost_type_II"] = vehicle_cost_type_II
            quartier_results["num_vehicles"] = num_vehicles

        results.append(quartier_results)
        result = quartier_results
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
        print(
            Fore.GREEN + f"Temps de déneigement avec véhicules type I : {result['time_type_I']:.2f} heures" + Style.RESET_ALL)
        print(
            Fore.GREEN + f"Temps de déneigement avec véhicules type II : {result['time_type_II']:.2f} heures" + Style.RESET_ALL)
        print(
            Fore.CYAN + f"Nombre de déneigeuses utilisées : {result['num_vehicles']}" + Style.RESET_ALL)

        visualizer = GraphVisualizerPlotly(graph_quartier)
        visualizer.visualize_results(drone_path_quartier, circuits, f"{quartier.replace(', Montreal, Canada', '').replace(' ', '_')}_{num_vehicles}_vehicules")
        break


    # Afficher le résumé final
    print(Fore.CYAN + "\nRésumé des opérations de déneigement pour tous les quartiers :" + Style.RESET_ALL)
    total_drone_cost = 0
    total_vehicle_cost_type_I = 0
    total_vehicle_cost_type_II = 0

    for result in results:
        total_drone_cost += result["drone_cost"]
        total_vehicle_cost_type_I += result["vehicle_cost_type_I"]
        total_vehicle_cost_type_II += result["vehicle_cost_type_II"]

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
        print(
            Fore.GREEN + f"Temps de déneigement avec véhicules type I : {result['time_type_I']:.2f} heures" + Style.RESET_ALL)
        print(
            Fore.GREEN + f"Temps de déneigement avec véhicules type II : {result['time_type_II']:.2f} heures" + Style.RESET_ALL)
        print(
            Fore.CYAN + f"Nombre de déneigeuses utilisées : {result['num_vehicles']}" + Style.RESET_ALL)

    print(Fore.CYAN + "\n\n-----------------------------------------\n\nCoût total des opérations de déneigement :" + Style.RESET_ALL)
    print(Fore.BLUE +
        f"Coût total du vol du drone : {total_drone_cost:.2f} €" + Style.RESET_ALL)
    print(Fore.RED +
        f"Coût total des opérations de déneigement avec véhicules type I : {total_vehicle_cost_type_I:.2f} €" + Style.RESET_ALL)
    print(Fore.RED +
        f"Coût total des opérations de déneigement avec véhicules type II : {total_vehicle_cost_type_II:.2f} €" + Style.RESET_ALL)


if __name__ == "__main__":
    main()
