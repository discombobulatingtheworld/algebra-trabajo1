# Algebra Aplicada - Trabajo 1

Este repositorio contiene una entrega para el trabajo 1 de la materia Algebra Aplicada de la carrera de Ingenieria en Informática de la Universidad Católica del Uruguay, cursada en el semestre 2 del año 2023.

La entrega consiste en un programa escrito en Python que permite realizar un análisis de sentimientos de un set de tweets, utilizando algebra de vectores.

## Equipo
- Armando Hernandez
- Franco De Estefano
- Rodrigo Jauregui

## Requerimientos

- [Python 3.11](https://www.python.org/downloads/release/python-3110/)

## Entorno virtual (Opcional)

Se recomienda utilizar un entorno virtual para instalar las dependencias del proyecto.

1. Crear un entorno virtual
```bash
python -m venv .venv
```
2. Activar el entorno virtual
```bash
source .venv\Scripts\activate
```

Para desactivar el entorno virtual, ejecutar el siguiente comando:
```bash
deactivate
```

## Instalación

1. Clonar el repositorio
```bash
git clone https://github.com/discombobulatingtheworld/algebra-trabajo1.git
```
2. Instalar las dependencias
```bash
pip install -r requirements.txt
```

## Uso

1. Ejecutar el programa
```bash
python program.py
```

## Argumentos

El programa acepta los siguientes argumentos:

- `-h, --help`: Muestra la ayuda del programa
- `-i, --input`: Ruta al directorio que contiene los archivos de tweets y palabras. Por defecto: `./input`
- `-o, --output`: Ruta al directorio donde se guardaran los archivos de salida. Por defecto: `./output`
- `-y, --yes`: No solicita confirmación para procesar los archivos.
- `-v, --verbose`: Muestra información adicional durante la ejecución del programa.

## Ejemplos

- Ejecutar el programa con los archivos de entrada en el directorio `./input` y los archivos de salida en el directorio `./output`:
```bash
python program.py
```

- Ejecutar el programa con los archivos de entrada en el directorio `./input` y los archivos de salida en el directorio `./output`, sin solicitar confirmación para procesar los archivos:
```bash
python program.py -y
```

- Ejecutar el programa con los archivos de entrada en el directorio `./input` y los archivos de salida en el directorio `./output`, sin solicitar confirmación para procesar los archivos y mostrando información adicional durante la ejecución del programa:
```bash
python program.py -y -v
```

- Ejecutar el programa con los archivos de entrada en el directorio `./data` y los archivos de salida en el directorio `./results`:
```bash
python program.py -i ./data -o ./results
```



