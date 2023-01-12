import json
import os

from chirpy.databases.databases import database_lookup, database_exists

ANIMAL_GPT_DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'animal_gpt_2.json')

import logging

logger = logging.getLogger('chirpylogger')

# load food database
with open(ANIMAL_GPT_DATABASE_FILE) as f:
    animal_gpt = json.load(f)

@database_exists("animal_gpt")
def verify_animal_exists_gpt(animal_name : str):
    # TODO: less hacky
    if animal_name not in animal_gpt:
        animal_name = animal_name[:-1]
    return animal_name in animal_gpt.keys()

@database_lookup("animal_gpt")
def lookup_animal_gpt(animal_name : str):
    key = animal_name
    if animal_name not in animal_gpt:
        # hacky way to do sg/pl
        # TODO (Shashank): use singularize_pluralnoun logic from entitylinker after speaking with Haojun
        if animal_name[:-1] in animal_gpt:
            key = animal_name[:-1]
    return animal_gpt[key]
