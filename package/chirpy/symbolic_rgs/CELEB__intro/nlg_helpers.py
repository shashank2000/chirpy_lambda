from chirpy.response_generators.celeb import celeb_helper
from chirpy.core.response_generator import nlg_helper

"""
    Getting the information on the celebrity
"""


@nlg_helper
def get_celeb_name(celeb):
    if celeb is None:
        return "None"
    return celeb.name

@nlg_helper
def get_celeb_pronoun(celeb):
    if celeb is None:
        return "them"
    return celeb_helper.find_celeb_pronoun(celeb.name)

@nlg_helper
def get_celeb_work_type(celeb):
    if celeb is None:
        return None
    return celeb_helper.find_celeb_type(celeb.name)

@nlg_helper
def sample_celeb_movie(celeb):
    if celeb is None:
        return None
    return celeb_helper.sample_celeb_work(celeb.name, "films")

@nlg_helper
def sample_celeb_song(celeb):
    if celeb is None:
        return None
    return celeb_helper.sample_celeb_work(celeb.name, "songs")

@nlg_helper
def sample_celeb_tv(celeb):
    if celeb is None:
        return None
    return celeb_helper.sample_celeb_work(celeb.name, "tv")

@nlg_helper
def sample_celeb_character(celeb):
    if celeb is None:
        return None
    return celeb_helper.sample_celeb_work(celeb.name, "characters")

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


@nlg_helper
def decide_type(work_type, type_name):
    return work_type == type_name
