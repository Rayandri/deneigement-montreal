
# Optimisation des trajets de déneigement pour la ville de Montréal

Ce projet vise à optimiser les trajets des équipes de déneigement de la ville de Montréal en utilisant les données d'OpenStreetMap et des algorithmes de parcours de graphes.

## Prérequis

- Python 3.7 ou supérieur
- `virtualenv` pour créer un environnement virtuel

## Installation

1. Clonez le dépôt :
   ```bash
   git clone <url-du-repo>
   cd <nom-du-repo>
   ```

2. Créez un environnement virtuel :
   ```bash
   python3 -m venv env
   source env/bin/activate   # Sur Windows utilisez `env\Scripts\activate`
   ```

3. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

## Utilisation

1. Assurez-vous que l'environnement virtuel est activé :
   ```bash
   source env/bin/activate   # Sur Windows utilisez `env\Scripts\activate`
   ```

2. Exécutez le script principal :
   ```bash
   python main.py
   ```

## Structure du projet

- `main.py` : Script principal pour télécharger, eulériser et segmenter le graphe de Montréal.
- `requirements.txt` : Fichier listant les dépendances nécessaires.
- `README.md` : Ce fichier d'explication.

## Fonctionnalités

- **GraphManager** : Télécharge ou charge le graphe de Montréal.
- **GraphEulirizer** : Eulérise le graphe pour garantir qu'il contient un circuit eulérien.
- **GraphSegmenter** : Segmente le graphe en sous-graphes par quartiers.

