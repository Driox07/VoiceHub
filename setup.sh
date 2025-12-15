#!/bin/bash

# Nombre del entorno virtual
VENV_DIR=".venv"

# Crear el entorno virtual
echo "Creando el entorno virtual..."
python3 -m venv $VENV_DIR

# Activar el entorno virtual
echo "Activando el entorno virtual..."
source $VENV_DIR/bin/activate

# Instalar dependencias
echo "Instalando dependencias..."
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "Archivo requirements.txt no encontrado. Asegúrate de agregar tus dependencias."
fi

# Iniciar la aplicación
echo "Iniciando la aplicación..."
python run.py