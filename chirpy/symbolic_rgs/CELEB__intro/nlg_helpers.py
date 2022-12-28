from chirpy.response_generators.celeb import celeb_helper
from chirpy.core.response_generator import nlg_helper

@nlg_helper
def get_celeb_pronoun(rg, celeb):
    return celeb_helper.find_celeb_pronoun(celeb)

@nlg_helper
def get_celeb_work_type(rg, celeb):
    return celeb_helper.find_celeb_type(celeb)

@nlg_helper
def sample_celeb_movie(rg, celeb):
    return celeb_helper.sample_celeb_work(celeb, "films")

@nlg_helper
def sample_celeb_song(rg, celeb):
    return celeb_helper.sample_celeb_work(celeb, "songs")

@nlg_helper
def sample_celeb_tv(rg, celeb):
    return celeb_helper.sample_celeb_work(celeb, "tv")

@nlg_helper
def sample_celeb_character(rg, celeb):
    return celeb_helper.sample_celeb_work(celeb, "characters")