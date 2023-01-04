import logging
import random
import pickle as pkl

from chirpy.core.response_generator import nlg_helper

CITY_INFO_PATH = "/Users/virginiaadams/chirpycardinal/chirpy/symbolic_rgs/PLACES__intro/city_info.pkl"

logger = logging.getLogger('chirpylogger')
city_info = pkl.load(open(CITY_INFO_PATH, "rb"))

@nlg_helper
def get_city_comment(city):
    city = city.lower()
    if city in city_info:
        city_data = city_info[city]
        logger.info(f"Loading intro comment for PLACE {city}")
        
        return random.choice(city_data["intro"])
    
    return None

