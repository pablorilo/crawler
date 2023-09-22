#!/bin/bash

source crawler_env/bin/activate

# Verifica si el entorno virtual está activo
if [[ "$VIRTUAL_ENV" == "" ]]; then
  echo "El entorno virtual NO está activo."
else
  echo "El entorno virtual está activo."
fi

# Ejecuta la aplicación
python3 main.py