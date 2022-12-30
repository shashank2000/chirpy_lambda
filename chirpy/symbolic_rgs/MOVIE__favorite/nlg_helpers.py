from chirpy.response_generators.movie import movie_helpers
from chirpy.core.response_generator import nlg_helper
from chirpy.response_generators.movie.expression_lists import YES, NO

import logging
import re

logger = logging.getLogger('chirpylogger')


@nlg_helper
def enterMovie(entity):
    print(entity.__dict__)
    logger.warning('entity is %s' % entity.talkable_name)
    return entity.talkable_name