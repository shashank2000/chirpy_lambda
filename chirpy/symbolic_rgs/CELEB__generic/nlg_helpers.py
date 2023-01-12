from chirpy.response_generators.celeb import celeb_helper
from chirpy.core.response_generator import nlg_helper

@nlg_helper
def get_celeb_opinion(celeb_name: str):
    return "I have liked " + celeb_name + " for quite some time now!"