"""Programa para el análisis de sentimientos en tweets.

Este programa permite analizar los sentimientos de un conjunto de tweets
utilizando un diccionario de palabras previamente clasificadas.

El programa recibe como entrada un archivo de texto con los tweets a analizar
y un archivo JSON con el diccionario de palabras clasificadas.

El formato del archivo de texto es un tweet por línea. El formato del archivo
JSON es un diccionario de listas, donde existen 3 listas: positivas, negativas
y neutrales. Cada lista contiene palabras clasificadas como positivas, negativas
y neutrales respectivamente. Las claves son: 'positive', 'negative' y 'neutral'.

"""

import sys
import os
import json
import argparse
import unicodedata
import numpy as np
import slugify as slg
import pandas as pd
from jsonschema import validate



DEFAULT_INPUT_PATH = 'input'
DEFAULT_OUTPUT_PATH = 'output'

TWEETS_FILE_NAME = 'tweets.txt'
WORDS_PATH = 'words.json'

OUTPUT_FILE_NAME = 'results.csv'

WORDS_JSON_SCHEMA = {
    'type': 'object',
    'properties': {
        'positive': {'type': 'array', 'items': {'type': 'string'}},
        'negative': {'type': 'array', 'items': {'type': 'string'}},
        'neutral': {'type': 'array', 'items': {'type': 'string'}},
    },
    'required': ['positive', 'negative', 'neutral'],
    'additionalProperties': False,
}

def sanitize_text(text: str) -> str:
    """Limpia un texto. Se remueven caracteres no alpha-numéricos y se convierte
    minúsculas. También se convierte todo carácter no ASCII a su equivalente
    ASCII.

    Args:
        text (str): Texto a limpiar.

    Returns:
        str: Texto limpio.
    """

    # Validaciones de parametros
    if not isinstance(text, str):
        raise TypeError('El texto debe ser un string.')
    
    # Limpia el text
    text = text.strip()
    text = text.lower()
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ASCII', 'ignore')
    text = text.decode('ASCII')
    text = slg.slugify(text)
    text = text.replace('-', ' ')

    return text

def load_tweets(path: str) -> list[str]:
    """Carga los tweets desde un archivo de texto.
    
    Args:
        path (str): Ruta al archivo de texto con los tweets.

    Returns:
        list: Lista de tweets.
    """

    # Validaciones de parametros
    if not isinstance(path, str):
        raise TypeError('El path debe ser un string.')
    if not path.endswith('.txt'):
        raise ValueError('El archivo debe ser un .txt')
    if not os.path.isfile(path):
        raise ValueError('El archivo no existe.')   
    
    # Carga los tweets
    tweets = []
    with open(path, 'r', encoding='utf-8') as file:
        for line in file:
            tweets.append(sanitize_text(line))

    return tweets

def load_words(path: str) -> dict[str, list[str]]:
    """Carga las palabras desde un archivo JSON.
    
    Args:
        path (str): Ruta al archivo JSON con las palabras.

    Returns:
        list: Lista de palabras positivas.
        list: Lista de palabras negativas.
        list: Lista de palabras neutrales.
        list: Lista de todas las palabras.
    """

    # Validaciones de parametros
    if not isinstance(path, str):
        raise TypeError('El path debe ser un string.')
    if not path.endswith('.json'):
        raise ValueError('El archivo debe ser un .json')
    if not os.path.isfile(path):
        raise ValueError('El archivo no existe.')
    
    # Carga las palabras
    words = {}
    with open(path, 'r', encoding='utf-8') as file:
        words = json.load(file)

    # Validaciones de formato
    try:
        validate(instance=words, schema=WORDS_JSON_SCHEMA)
    except Exception as e:
        raise ValueError('El archivo no tiene el formato correcto.') from e
    
    # Validaciones de contenido
    if not words['positive']:
        raise ValueError('El archivo no contiene palabras positivas.')
    if not words['negative']:
        raise ValueError('El archivo no contiene palabras negativas.')
    if not words['neutral']:
        raise ValueError('El archivo no contiene palabras neutrales.')
    
    # Crea las listas de palabras
    positive = words['positive']
    negative = words['negative']
    neutral = words['neutral']

    # Limpiar las palabras
    positive = [sanitize_text(word) for word in positive]
    negative = [sanitize_text(word) for word in negative]
    neutral = [sanitize_text(word) for word in neutral]

    # Crea la lista de todas las palabras
    all_words = positive + negative + neutral

    # MAS validaciones de contenido
    if len(all_words) != len(set(all_words)):
        raise ValueError('El archivo contiene palabras repetidas.')
    
    return positive, negative, neutral, all_words

def get_count_vector(text: str, words: list) -> np.ndarray[int]:
    """Crea un vector para un texto dado un conjunto de palabras, indicando
    cuantas veces aparece cada palabra en el texto. El orden de las palabras
    en el vector es el mismo que el orden en el que aparecen en el conjunto
    de palabras.

    Args:
        text (str): Texto a vectorizar.
        words (list): Conjunto de palabras.

    Returns:
        np.ndarray[int]: Vector de conteo.
    """

    # Validaciones de parametros
    if not isinstance(text, str):
        raise TypeError('El texto debe ser un string.')
    if not isinstance(words, list):
        raise TypeError('El conjunto de palabras debe ser una lista.')
    if not words:
        raise ValueError('El conjunto de palabras no puede estar vacío.')
    if not all(isinstance(word, str) for word in words):
        raise TypeError('El conjunto de palabras debe contener strings.')
    if not all(word.isalpha() for word in words):
        raise ValueError('El conjunto de palabras debe contener palabras.')

    # Crea el vector
    count_vector = np.zeros((len(words),), dtype=int)

    # Cuenta las palabras
    for word in text.split():
        for i, w in enumerate(words):
            if w == word:
                count_vector[i] = count_vector[i] + 1
    
    return count_vector

def get_classification_vector(positive_words: list, neutral_words: list, negative_words: list, text: str) -> np.ndarray[int]:
    """Crea un vector de clasificación para un texto dado un conjunto de palabras
    positivas, negativas y neutrales. El vector de clasificación indica cuantas
    palabras positivas, negativas y neutrales hay en el texto.

    Args:
        positive_words (list): Conjunto de palabras positivas.
        negative_words (list): Conjunto de palabras negativas.
        neutral_words (list): Conjunto de palabras neutrales.
        text (str): Texto a clasificar.

    Returns:
        np.ndarray[int]: Vector de clasificación.
    """

    # Validaciones de parametros
    if not isinstance(positive_words, list):
        raise TypeError('El conjunto de palabras positivas debe ser una lista.')
    if not isinstance(negative_words, list):
        raise TypeError('El conjunto de palabras negativas debe ser una lista.')
    if not isinstance(neutral_words, list):
        raise TypeError('El conjunto de palabras neutrales debe ser una lista.')
    if not isinstance(text, str):
        raise TypeError('El texto debe ser un string.')
    if not positive_words:
        raise ValueError('El conjunto de palabras positivas no puede estar vacío.')
    if not negative_words:
        raise ValueError('El conjunto de palabras negativas no puede estar vacío.')
    if not neutral_words:
        raise ValueError('El conjunto de palabras neutrales no puede estar vacío.')
    if not all(isinstance(word, str) for word in positive_words):
        raise TypeError('El conjunto de palabras positivas debe contener strings.')
    if not all(isinstance(word, str) for word in negative_words):
        raise TypeError('El conjunto de palabras negativas debe contener strings.')
    if not all(isinstance(word, str) for word in neutral_words):
        raise TypeError('El conjunto de palabras neutrales debe contener strings.')
    if not all(word.isalpha() for word in positive_words):
        raise ValueError('El conjunto de palabras positivas debe contener palabras.')
    if not all(word.isalpha() for word in negative_words):
        raise ValueError('El conjunto de palabras negativas debe contener palabras.')
    if not all(word.isalpha() for word in neutral_words):
        raise ValueError('El conjunto de palabras neutrales debe contener palabras.')

    # Crea el vector
    classification_vector = np.zeros((3,), dtype=int)

    # Cuenta las palabras
    for current_word in text.split():
        for _, word in enumerate(positive_words):
            if word == current_word:
                classification_vector[0] = classification_vector[0] + 1
        for _, word in enumerate(neutral_words):
            if word == current_word:
                classification_vector[1] = classification_vector[1] + 1
        for _, word in enumerate(negative_words):
            if word == current_word:
                classification_vector[2] = classification_vector[2] + 1

    return classification_vector

def process_tweet(tweet: str, positive_words: list[str], negative_words: list[str], neutral_words: list[str], all_words: list[str]) -> (int, float):
    """Procesa un tweet y realiza un análisis de sentimientos. El análisis de
    sentimientos se realiza a partir de un conjunto de palabras positivas,
    negativas y neutrales.

    Args:
        tweet (str): Tweet a analizar.
        positive_words (list): Conjunto de palabras positivas.
        negative_words (list): Conjunto de palabras negativas.
        neutral_words (list): Conjunto de palabras neutrales.
        all_words (list): Conjunto de todas las palabras.

    Returns:
        int: Puntuación del tweet.
        float: Indice de calidad del resultado.
    """

    # Validaciones de parametros
    if not isinstance(tweet, str):
        raise TypeError('El tweet debe ser un string.')
    if not isinstance(positive_words, list):
        raise TypeError('El conjunto de palabras positivas debe ser una lista.')
    if not isinstance(negative_words, list):
        raise TypeError('El conjunto de palabras negativas debe ser una lista.')
    if not isinstance(neutral_words, list):
        raise TypeError('El conjunto de palabras neutrales debe ser una lista.')
    if not isinstance(all_words, list):
        raise TypeError('El conjunto de palabras debe ser una lista.')
    if not tweet:
        raise ValueError('El tweet no puede estar vacío.')
    if not positive_words:
        raise ValueError('El conjunto de palabras positivas no puede estar vacío.')
    if not negative_words:
        raise ValueError('El conjunto de palabras negativas no puede estar vacío.')
    if not neutral_words:
        raise ValueError('El conjunto de palabras neutrales no puede estar vacío.')
    if not all_words:
        raise ValueError('El conjunto de palabras no puede estar vacío.')
    if not all(isinstance(word, str) for word in positive_words):
        raise TypeError('El conjunto de palabras positivas debe contener strings.')
    if not all(isinstance(word, str) for word in negative_words):
        raise TypeError('El conjunto de palabras negativas debe contener strings.')
    if not all(isinstance(word, str) for word in neutral_words):
        raise TypeError('El conjunto de palabras neutrales debe contener strings.')
    if not all(isinstance(word, str) for word in all_words):
        raise TypeError('El conjunto de palabras debe contener strings.')
    if not all(word.isalpha() for word in positive_words):
        raise ValueError('El conjunto de palabras positivas debe contener palabras.')
    if not all(word.isalpha() for word in negative_words):
        raise ValueError('El conjunto de palabras negativas debe contener palabras.')
    if not all(word.isalpha() for word in neutral_words):
        raise ValueError('El conjunto de palabras neutrales debe contener palabras.')
    if not all(word.isalpha() for word in all_words):
        raise ValueError('El conjunto de palabras debe contener palabras.')
    
    # Crea el vector de conteo
    count_vector = get_count_vector(tweet, all_words)

    # Crea el vector de clasificación
    classification_vector = get_classification_vector(positive_words, neutral_words, negative_words, tweet)

    # Crea un vector de pesos
    weight_vector = np.array([1, 0, -1])

    # Calcula el valor del tweet
    score = classification_vector.T @ weight_vector

    # Calcula el indice de calidad
    quality_index = sum(np.dot((1/len(all_words)), count_vector))

    return score, quality_index


def main():
    """Función principal del programa."""

    # Parsea los argumentos
    parser = argparse.ArgumentParser(description='Analiza los sentimientos de un conjunto de tweets.', add_help=True)
    parser.add_argument('-i', '--input', type=str, default=DEFAULT_INPUT_PATH, help='Ruta al directorio de entrada.')
    parser.add_argument('-o', '--output', type=str, default=DEFAULT_OUTPUT_PATH, help='Ruta al directorio de salida.')
    parser.add_argument('-y', '--yes', action='store_true', help='No solicita confirmación al usuario.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Muestra información adicional.')
    args = parser.parse_args()

    # Validaciones de parametros
    if not os.path.isdir(args.input):
        raise ValueError('El directorio de entrada no existe.')
    if not os.path.isfile(os.path.join(args.input, TWEETS_FILE_NAME)):
        raise ValueError('El archivo de tweets no existe.')
    if not os.path.isfile(os.path.join(args.input, WORDS_PATH)):
        raise ValueError('El archivo de palabras no existe.')
    if not os.path.isdir(args.output):
        raise ValueError('El directorio de salida no existe.')
    if not os.access(args.output, os.W_OK):
        raise ValueError('El directorio de salida no tiene permisos de escritura.')
    
    # Si verboso, muestra un mensaje de inicio
    if args.verbose:
        print('Iniciando análisis de sentimientos...')
        print()
    
    # Verificar con el usuario si desea continuar con los valores establecidos
    if not args.yes:
        print('Directorio de entrada:', os.path.abspath(args.input))
        print('Directorio de salida:', os.path.abspath(args.output))
        print('¿Desea continuar? [Y/n]', end=' ')
        response = input()
        if response.lower() not in ('', 'y', 'yes'):
            print('Abortando...')
            sys.exit(0)
        else:
            print()

    # Carga los tweets
    tweets = load_tweets(os.path.join(args.input, TWEETS_FILE_NAME))

    # Carga las palabras
    positive_words, negative_words, neutral_words, all_words = load_words(os.path.join(args.input, WORDS_PATH))

    # Procesa los tweets
    results: list[(str, int, float)] = []
    for tweet in tweets:
        score, quality_index = process_tweet(tweet, positive_words, negative_words, neutral_words, all_words)
        results.append((tweet, score, quality_index))

    # Crea un DataFrame con los resultados
    df = pd.DataFrame(results, columns=['Tweet', 'Puntuacion', 'Indice de Calidad'])

    # Si verboso, muestra los resultados
    if args.verbose:
        print('Resultados:')
        print(df)
        print()
    
    # Guarda los resultados
    with open(os.path.join(args.output, OUTPUT_FILE_NAME), 'w') as file:
        df.to_csv(file, index=False, encoding='utf-8')

    # Si verboso, muestra la ruta del archivo de salida
    if args.verbose:
        print('Archivo de salida:', os.path.abspath(os.path.join(args.output, OUTPUT_FILE_NAME)))


if __name__ == '__main__':
    main()