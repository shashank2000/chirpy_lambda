from chirpy.response_generators.movie import movie_helpers
from chirpy.core.response_generator import nlg_helper
from chirpy.response_generators.movie.expression_lists import YES, NO

import logging
import re

logger = logging.getLogger('chirpylogger')


def found_phrase(phrase, response):
    return re.search(f'(\A| ){phrase}(\Z| )', response) is not None


@nlg_helper
def set_whether_user_likes_movie(flag):
    logger.warning('flag is %s' % flag)
    logger.warning('flag type is %s' % type(flag))
    if flag:
        logger.primary_info('Setting state to True!')
    else:
        logger.primary_info('Setting state to False!')
    return flag