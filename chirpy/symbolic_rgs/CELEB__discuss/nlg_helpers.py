from chirpy.response_generators.celeb import celeb_helper
from chirpy.core.response_generator import nlg_helper
from chirpy.core.entity_linker.entity_linker_classes import WikiEntity


@nlg_helper
def extract_work_name(work):
    if isinstance(work, WikiEntity):
        return work.name
    return "UNKNOWN"


@nlg_helper
def is_known_work(work):
    if work is None:
        return False
    if isinstance(work, WikiEntity):
        return celeb_helper.is_known_film_tv_song(work.name)
    return False


@nlg_helper
def find_opinion(work: str, celeb_name: str):
    return celeb_helper.find_celeb_opinion(work, celeb_name)