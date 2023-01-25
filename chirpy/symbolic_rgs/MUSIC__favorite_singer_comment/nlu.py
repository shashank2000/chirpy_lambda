from chirpy.core.response_generator.nlu import nlu_processing
from chirpy.response_generators.music.expression_lists import PositiveTemplate, NegativeTemplate

@nlu_processing
def get_flags(context):
    slots_disagree = NegativeTemplate().execute(context.utterance)
    if slots_disagree is not None:
        ADD_NLU_FLAG('MUSIC__user_disagree')

@nlu_processing
def get_background_flags(context):
    return

