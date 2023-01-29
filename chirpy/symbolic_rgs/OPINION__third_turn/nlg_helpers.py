import logging
import random
import json
from chirpy.core.entity_linker.entity_linker_classes import PseudoEntity

logger = logging.getLogger("chirpylogger")

PATH = "chirpy/symbolic_data/opinions/opionable_labeled_final.json"
with open(PATH, "r") as f:
    activities = json.load(f)


def get_topic_type(topic: str):
    return activities[topic]


def get_opinion(input=""):
    for topic in activities.keys():
        if topic in input:
            return PseudoEntity(topic)
    return PseudoEntity(random.choice(list(activities.keys())))


def opinion_exists(input=""):
    for topic in activities.keys():
        if topic in input:
            return True
    return False
