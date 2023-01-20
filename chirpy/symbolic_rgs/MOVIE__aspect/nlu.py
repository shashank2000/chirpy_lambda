from chirpy.core.response_generator.nlu import nlu_processing
import logging

logger = logging.getLogger('chirpylogger')


@nlu_processing
def get_flags(context):
    dialog_act = context.state_manager.current_state.dialogact
    if dialog_act['top_1'] == 'opinion':
        ADD_NLU_FLAG('MOVIE__user_mentioned_reason', True)
    ADD_NLU_FLAG('MOVIE__last_utterance', context.utterance)