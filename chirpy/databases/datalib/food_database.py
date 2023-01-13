import json
import os

from chirpy.databases.databases import database_lookup, database_exists

FOOD_DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'json/foods.json')
FOOD_GPT_DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'json/food_gpt_partial.json')

import logging

logger = logging.getLogger('chirpylogger')


# load food database
with open(FOOD_DATABASE_FILE) as f:
    food = json.load(f)

@database_exists("food")
def verify_food_exists(food_name : str):
    return food_name in food

@database_lookup("food")
def lookup_food(food_name : str):
    return food[food_name]

# load food database
with open(FOOD_GPT_DATABASE_FILE) as f:
    food_gpt = json.load(f)

@database_exists("food_gpt")
def verify_food_exists_gpt(food_name : str):
    return food_name in food_gpt.keys()

@database_lookup("food_gpt")
def lookup_food_gpt(food_name : str):
    return food_gpt[food_name]
