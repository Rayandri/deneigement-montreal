#!/bin/bash

# Définir le nom de l'environnement virtuel
VENV_DIR="env"

# Vérifier si l'environnement virtuel existe, sinon le créer
if [ ! -d "$VENV_DIR" ]; then
    echo "Création de l'environnement virtuel..."
    python3 -m venv $VENV_DIR
    echo "Environnement virtuel créé."
fi

# Activer l'environnement virtuel
source $VENV_DIR/bin/activate

# Mettre à jour pip
pip install --upgrade pip

# Installer les dépendances à partir de requirements.txt
pip install -r requirements.txt

# Installer pyconcorde depuis GitHub
pip install 'pyconcorde @ git+https://github.com/jvkersch/pyconcorde'

echo "Installation terminée."
