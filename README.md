
# Deneigement Montreal

## Description
Ce projet vise à optimiser les trajets des opérations de déneigement de la ville de Montréal. Il utilise des algorithmes avancés pour résoudre les problèmes du postier chinois et d'optimisation de parcours de drones afin de minimiser les coûts et d'améliorer l'efficacité des opérations de déneigement.

## Algorithmes Utilisés
1. **Problème du Postier Chinois** : Utilisé pour optimiser les trajets des véhicules de déneigement en assurant que chaque rue est parcourue au moins une fois de manière efficace.
   
2. **Optimisation des Parcours de Drones** : Utilisé pour optimiser les trajets des drones en utilisant une version modifiée du problème du postier chinois pour couvrir toutes les zones de manière efficace.

## Historique des Algorithmes

### Algorithmes Anciens
- **Concorde TSP Solver** : Utilisé pour résoudre le problème TSP avec une efficacité optimale. Concorde est l'un des solveurs TSP les plus rapides et les plus précis disponibles.
- **OR-Tools pour VRP** : Utilisé pour résoudre le problème de routage des véhicules. OR-Tools est une suite d'optimisation de Google, connue pour ses performances élevées et sa capacité à traiter de grands ensembles de données rapidement et efficacement.

### Algorithmes Actuels
- **Problème du Postier Chinois** : Plus adapté pour les opérations de déneigement car il permet de s'assurer que chaque rue est parcourue au moins une fois sans nécessiter un retour au point de départ après chaque rue.
- **Optimisation des Parcours de Drones** : Permet de couvrir toutes les zones nécessitant un déneigement de manière efficace et économique.

### Pourquoi les Nouveaux Algorithmes ?
Les nouveaux algorithmes ont été choisis car ils offrent une meilleure adéquation avec les exigences spécifiques des opérations de déneigement, notamment la couverture complète des zones avec un minimum de répétitions et de coûts.

## Installation
Pour installer toutes les dépendances nécessaires et configurer l'environnement, suivez les étapes ci-dessous.

### Étapes d'Installation

1. **Clonez le dépôt** :
    \`\`\`bash
    git clone https://github.com/Rayandri/deneigement-montreal.git
    cd deneigement-montreal
    \`\`\`

2. **Créez et activez un environnement virtuel, et installez les dépendances** :
    \`\`\`bash
    ./install.sh
    \`\`\`

    ou bien manuellement :

   Pour créer un environnement virtuel :
   \`\`\`bash
      python3 -m venv env
      source env/bin/activate
   \`\`\`

   Puis installez les dépendances :
    \`\`\`bash
    pip install -r requirements.txt
    \`\`\`

## Utilisation
Le script principal se trouve dans \`main.py\`. Pour exécuter le script, utilisez la commande suivante :

\`\`\`bash
source env/bin/activate
python main.py
\`\`\`

## Structure du Code
- \`GraphManager\`: Gère le téléchargement, le chargement, l'eulérisation et l'optimisation des trajets dans un graphe urbain.
- \`GraphVisualizerPlotly\`: Gère la visualisation et l'animation des graphes avec un fond de carte OpenStreetMap.
- \`optimize_drone_path\`: Optimise le trajet du drone en utilisant une version modifiée du problème du postier chinois.

## Fonctionnalités
- **Téléchargement et Chargement de Graphes** : Télécharge les graphes urbains depuis OpenStreetMap et les charge pour utilisation.
- **Eulerisation de Graphes** : Modifie les graphes pour les rendre eulériens, permettant ainsi de résoudre efficacement le problème du postier chinois.
- **Optimisation des Parcours** : Utilise des algorithmes avancés pour optimiser les parcours des drones et des véhicules de déneigement.
- **Visualisation Interactive** : Utilise Plotly pour animer et visualiser les trajets optimisés sur un fond de carte OpenStreetMap.

## Exemple de Résultats
Le script produit des visualisations animées des trajets optimisés pour chaque quartier, montrant comment les drones et les véhicules de déneigement couvrent les zones assignées.
