from chirpy.core.response_generator import nlg_helper
from chirpy.core.entity_linker.entity_groups import EntityGroupsForExpectedType
import re

def set_favorite_movie(cur_entity):
    if not cur_entity:
        return None
    if EntityGroupsForExpectedType.film.matches(cur_entity):
        return cur_entity
    return None

    