from chirpy.core.response_generator import nlg_helper
import logging
import re

logger = logging.getLogger("chirpylogger")


@nlg_helper
def set_whether_user_likes_movie(flag):
    return flag
    