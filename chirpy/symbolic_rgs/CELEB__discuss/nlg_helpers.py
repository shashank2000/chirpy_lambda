from chirpy.response_generators.celeb import celeb_helper
from chirpy.core.response_generator import nlg_helper
from chirpy.core.entity_linker.entity_linker_classes import PseudoEntity


@nlg_helper
def extract_work_name(work):
    if isinstance(work, PseudoEntity):
        return work.name
    return "UNKNOWN"


@nlg_helper
def is_known_work(work):
    if work is None:
        return False
    if isinstance(work, PseudoEntity):
        return celeb_helper.is_known_film_tv_song(work.name)
    return False


@nlg_helper
def is_same_work(bot_work_1, bot_work_2, bot_work_3, user_work):
    if user_work is None:
        return False
    for bw in [bot_work_1, bot_work_2, bot_work_3]:
        if bw is None:
            continue
        if bw == user_work:
            return True
    return False



@nlg_helper
def find_opinion(work: str, celeb_name: str):
    return celeb_helper.find_celeb_opinion(work, celeb_name)