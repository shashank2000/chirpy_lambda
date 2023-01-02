from chirpy.response_generators.celeb import celeb_helper
from chirpy.core.response_generator import nlg_helper


@nlg_helper
def is_known_work(work: str):
    return celeb_helper.is_known_film_tv_song(work)


@nlg_helper
def find_opinion(work: str, celeb_name: str):
    return celeb_helper.find_celeb_opinion(work, celeb_name)