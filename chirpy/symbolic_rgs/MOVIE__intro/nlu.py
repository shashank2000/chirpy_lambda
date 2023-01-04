from chirpy.response_generators.movie import movie_helpers
from chirpy.core.response_generator.nlu import nlu_processing
import logging

logger = logging.getLogger('chirpylogger')


@nlu_processing
def get_flags(context):
    pos_val = context.flags['GlobalFlag__YES']
    # neg_val = context.flags['GlobalFlag__NO']
    # logger.warning(f'Positive response is {pos_val}')
    # logger.warning(f'Negative response is {neg_val}')
    logger.warning(f'User responded {pos_val} to the question "Do you like watching movies?"')
    ADD_NLU_FLAG('MOVIE__user_likes_movie', pos_val)
    # if movie_helpers.is_positive(rg, utterance):
    #     logger.primary_info('A positive response was entered by the user.')
    #     ADD_NLU_FLAG('MOVIE__user_likes_movie', True)
    # else:
    #     logger.primary_info('A negative response was entered by the user.')
    #     ADD_NLU_FLAG('MOVIE__user_likes_movie', False)

@nlu_processing
def get_background_flags(context):
    return