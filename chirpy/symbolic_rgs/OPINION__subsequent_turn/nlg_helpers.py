from chirpy.core.response_generator import nlg_helper

import logging
import random
import json

logger = logging.getLogger('chirpylogger')

PATH = 'chirpy/symbolic_data/opinions/opinions_final.json'
with open(PATH, 'r') as f:
    data = json.load(f)

# def get_random_opinion():
#     topics = list(data.keys())
#     return random.choice(topics)


response_tones = ['disagree', 'strong_disagree', 'agree']

@nlg_helper
def get_opinion_response(user_sentiment: str, topic: str):
    tone = random.choice(response_tones)
    if user_sentiment == "positive" or user_sentiment == "negative":
        return str(data[topic][user_sentiment][tone])
    return None