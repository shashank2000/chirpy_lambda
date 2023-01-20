from chirpy.response_generators.movie import movie_helpers
from chirpy.core.response_generator import nlg_helper
from chirpy.core.entity_linker.entity_groups import EntityGroupsForExpectedType

import logging
import re

logger = logging.getLogger("chirpylogger")


@nlg_helper
def set_favorite_movie(cur_entity):
    if not cur_entity:
        return None
    if EntityGroupsForExpectedType.film.matches(cur_entity):
        return cur_entity
    return None
