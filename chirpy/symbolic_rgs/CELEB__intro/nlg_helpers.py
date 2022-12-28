from chirpy.response_generators.celeb import celeb_helper
from chirpy.core.response_generator import nlg_helper

"""
    Getting the information on the celebrity
"""

@nlg_helper
def get_celeb_pronoun(celeb: str):
    return celeb_helper.find_celeb_pronoun(celeb)

@nlg_helper
def get_celeb_work_type(celeb: str):
    return celeb_helper.find_celeb_type(celeb)

@nlg_helper
def sample_celeb_movie(celeb: str):
    return celeb_helper.sample_celeb_work(celeb, "films")

@nlg_helper
def sample_celeb_song(celeb: str):
    return celeb_helper.sample_celeb_work(celeb, "songs")

@nlg_helper
def sample_celeb_tv(celeb: str):
    return celeb_helper.sample_celeb_work(celeb, "tv")

@nlg_helper
def sample_celeb_character(celeb: str):
    return celeb_helper.sample_celeb_work(celeb, "characters")

"""
    Grammatical helpers to get the pronouns right
"""

@nlg_helper
def pronoun_possessive_adjs(pronoun: str):
    if pronoun == "he":
        return "his"
    elif pronoun == "she":
        return "her"
    else:
        return "their"

@nlg_helper
def pronoun_obj(pronoun: str):
    if pronoun == "he":
        return "him"
    elif pronoun == "she":
        return "her"
    else:
        return "them"