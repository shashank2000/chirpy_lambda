from chirpy.response_generators.movie import movie_helpers
from chirpy.core.response_generator.nlu import nlu_processing
import logging

logger = logging.getLogger('chirpylogger')


@nlu_processing
def get_flags(context):
    logger.warning(f'context is {context}')
    dialog_act = context.state_manager.current_state.dialogact
    # logger.warning(f'context.state_manager.current_state[\'dialogact\'] is {dialog_act}')
    if dialog_act['top_1'] == 'opinion':
        ADD_NLU_FLAG('MOVIE__user_mentioned_reason', True)
    ADD_NLU_FLAG('MOVIE__last_utterance', context.utterance)


@nlu_processing
def get_background_flags(context):
    return


