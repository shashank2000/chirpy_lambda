import json
import os

from chirpy.databases.databases import database_lookup, database_exists

ANIMAL_GPT_DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'json/animal_gpt_2.json')

import logging

logger = logging.getLogger('chirpylogger')

# load food database
with open(ANIMAL_GPT_DATABASE_FILE) as f:
    animal_gpt = json.load(f)

@database_exists("animal_gpt")
def verify_animal_exists_gpt(animal_name : str):
    return animal_name in animal_gpt.keys()

@database_lookup("animal_gpt")
def lookup_animal_gpt(animal_name : str):
    return animal_gpt[animal_name]
