
# Deneigement Montreal

## Description
Ce projet vise à optimiser les trajets des opérations de déneigement de la ville de Montréal. Il utilise des algorithmes avancés pour résoudre les problèmes de TSP (Travelling Salesman Problem) et de VRP (Vehicle Routing Problem) afin de minimiser les coûts et d'améliorer l'efficacité des opérations de déneigement.

## Algorithmes Utilisés
1. **Concorde TSP Solver** : Utilisé pour résoudre le problème TSP avec une efficacité optimale. Concorde est l'un des solveurs TSP les plus rapides et les plus précis disponibles.
   
2. **OR-Tools pour VRP** : Utilisé pour résoudre le problème de routage des véhicules. OR-Tools est une suite d'optimisation de Google, connue pour ses performances élevées et sa capacité à traiter de grands ensembles de données rapidement et efficacement.

## Installation
Pour installer toutes les dépendances nécessaires et configurer l'environnement, suivez les étapes ci-dessous.

### Étapes d'Installation

1. **Clonez le dépôt** :
    ```bash
    git clone https://github.com/Rayandri/deneigement-montreal.git
    cd deneigement-montreal
    ```

2. **Créez et activez un environnement virtuel, et installez les dépendances** :
    - Assurez-vous que le fichier `requirements.txt` est présent dans le répertoire cloné.
    - Exécutez le script d'installation :

    ```bash
    ./install.sh
    ```


## Utilisation
Le script principal se trouve dans `main.py`. Pour exécuter le script, utilisez la commande suivante :

```bash
source venv/bin/activate
python main.py
```

## Structure du Code
- `GraphManager`: Gère le téléchargement et le chargement du graphe de la ville.
- `create_distance_matrix`: Crée une matrice de distances à partir du graphe.
- `optimize_drone_path`: Optimise le trajet du drone en utilisant le Concorde TSP Solver.
- `create_vrp_graph`: Crée un graphe VRP pour les nœuds nécessitant un déneigement.
- `solve_vrp`: Résout le VRP en utilisant OR-Tools.

## Contributions
Les contributions sont les bienvenues ! Veuillez soumettre une pull request ou ouvrir une issue pour toute suggestion ou amélioration.
