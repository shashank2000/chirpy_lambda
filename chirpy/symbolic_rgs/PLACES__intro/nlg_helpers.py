#from chirpy.response_generators.food.food_helpers import get_intro_acknowledgement, sample_food_containing_ingredient, get_attribute
from chirpy.response_generators.food import food_helpers 
from chirpy.core.response_generator import nlg_helper, nlg_helper_augmented
import logging
import random

logger = logging.getLogger('chirpylogger')

CITIES = {
    'New York': {
        'population': '8.5 million',
        'language': 'English'
    },
    
    'Beijing': {
        'population': '22 million',
        'language': 'Mandarin'
    },
    
    'Paris': {
        'population': '2.2 million',
        'language': 'French'
    },
    
    'Johannesburg': {
        'population': '5.63 million',
        'language': 'English and Zulu'
    },
    
    'Mumbai': {
        'population': '20.6 million',
        'language': 'Marathi, Hindi, English, and Gujarati'
    },
    
}

@nlg_helper
def get_city_population(rg, city): 
    if city in CITIES:
        city_data = CITIES[city]
        logger.warning(f"FACTOID includes POPULATION: {'population' in city_data}")
        if 'population' in city_data:
            return city_data['population']
    return None

@nlg_helper
def get_city_language(rg, city): 
    if city in CITIES:
        city_data = CITIES[city]
        logger.warning(f"FACTOID includes LANGUAGE: {'language' in city_data}")
        if 'language' in city_data:
            return city_data['language']
    return None


