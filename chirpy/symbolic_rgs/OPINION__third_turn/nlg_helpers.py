import logging
import random
import json

logger = logging.getLogger('chirpylogger')

PATH = 'chirpy/symbolic_data/opinions/opionable_labeled_final.json'
with open(PATH, 'r') as f:
    activities = json.load(f)

def get_topic_type(topic: str):
    return f"What other {activities[topic]} do you like?"

def get_opinion(input=""):
    for topic in activities.keys():
        if topic in input:
            return topic
    return random.choice(list(activities.keys()))
