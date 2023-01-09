import logging
import random
import json

logger = logging.getLogger('chirpylogger')

f = open('chirpy/symbolic_data/opinions/opinions_final.json')
data = json.load(f)
f.close()

# def get_random_opinion():
#     topics = list(data.keys())
#     return random.choice(topics)


response_tones = ['disagree', 'strong_disagree', 'agree']

def get_opinion_response(user_sentiment: str, topic: str):
    tone = random.choice(response_tones)
    if user_sentiment == "positive" or user_sentiment == "negative":
        return str(data[topic][user_sentiment][tone])
    return None
