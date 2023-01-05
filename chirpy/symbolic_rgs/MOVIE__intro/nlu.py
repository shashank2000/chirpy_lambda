from chirpy.response_generators.movie import movie_helpers
from chirpy.core.response_generator.nlu import nlu_processing
import logging

logger = logging.getLogger('chirpylogger')


@nlu_processing
def get_flags(context):
    pos_val = context.flags['GlobalFlag__YES']
    logger.warning(f'User responded {pos_val} to the question "Do you like watching movies?"')
    ADD_NLU_FLAG('MOVIE__user_likes_movie', pos_val)

@nlu_processing
def get_background_flags(context):
    return