from chirpy.core.response_generator import nlg_helper
import logging
import re

logger = logging.getLogger('chirpylogger')


@nlg_helper
def set_whether_user_likes_movie(flag):
    if flag:
        logger.primary_info('Setting state to True!')
    else:
        logger.primary_info('Setting state to False!')
    return flag
