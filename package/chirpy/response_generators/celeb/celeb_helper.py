import json
import logging
import random
import os
from os.path import abspath, dirname

logger = logging.getLogger("chirpylogger")

# CELEBS = ["taylor swift", "ryan reynolds", "nathan fillion", "matthew mcconaughey"]
CELEBS = json.load(open(os.path.join(abspath(dirname(__file__)), "reverse_filtered_celeb.json")))
OPINIONS = json.load(open(os.path.join(abspath(dirname(__file__)), "celeb_work_opinions.json")))


def is_known_celeb(entity_name):
    logger.primary_info(entity_name.lower() in CELEBS)
    logger.primary_info(entity_name)
    return entity_name.lower() in CELEBS


def is_known_film_tv_song(entity_name):
    return entity_name in OPINIONS


def find_celeb_opinion(work_name, celeb_name):
    work_opinions = OPINIONS[work_name]
    if celeb_name in work_opinions:
        return work_opinions[celeb_name]
    first_opinion = list(work_opinions.values())[0]
    return first_opinion


def find_celeb_pronoun(entity_name):
    if entity_name.lower() in CELEBS:
        return CELEBS[entity_name.lower()]["pronoun"]
    return "them"


def find_celeb_type(entity_name):
    # Decide based on total page views
    # Assuming this entity name we have in our celeb dictionary
    et_name = entity_name.lower()
    if et_name not in CELEBS:
        return "other"
    pg_cts_songs = sum([x[1] for x in CELEBS[et_name]["songs"]])
    pg_cts_films = sum([x[1] for x in CELEBS[et_name]["films"]])
    pg_cts_tv = sum(x[1] for x in CELEBS[et_name]["tv"])
    if pg_cts_songs > max(pg_cts_films, pg_cts_tv):
        return "song"
    elif pg_cts_films > max(pg_cts_tv, pg_cts_songs):
        return "movie"
    elif pg_cts_tv > max(pg_cts_films, pg_cts_songs):
        return "TV show"

    return "other"


def sample_celeb_work(celeb, type_work):
    if celeb.lower() not in CELEBS:
        return None
    all_celeb_work = CELEBS[celeb.lower()][type_work]
    if len(all_celeb_work) == 0:
        return None
    all_probs = [x[1] for x in all_celeb_work]
    # randomly sample weighted by page views
    random_sel_work = random.choices(all_celeb_work, weights=all_probs, k=1)[0][0]
    if "(" in random_sel_work:
        random_sel_work = random_sel_work[: random_sel_work.index("(")]
    return random_sel_work.strip()
