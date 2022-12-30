from chirpy.response_generators.movie import movie_helpers
from chirpy.core.response_generator.nlu import nlu_processing
import logging

logger = logging.getLogger('chirpylogger')


@nlu_processing
def get_flags(context):
    ADD_NLU_FLAG('MOVIE__user_likes_movie', True)
    # if movie_helpers.is_positive(rg, utterance):
    #     logger.primary_info('A positive response was entered by the user.')
    #     ADD_NLU_FLAG('MOVIE__user_likes_movie', True)
    # else:
    #     logger.primary_info('A negative response was entered by the user.')
    #     ADD_NLU_FLAG('MOVIE__user_likes_movie', False)

@nlu_processing
def get_background_flags(context):
    return