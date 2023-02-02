from chirpy.core.response_generator.nlu import nlu_processing
from chirpy.response_generators.music.regex_templates.heard_but_dont_like_song import HeardButDoNotLikeTemplate

@nlu_processing
def get_flags(context):
    slots_disagree = HeardButDoNotLikeTemplate().execute(context.utterance)
    if slots_disagree is not None:
        ADD_NLU_FLAG('MUSIC__user_heard_but_do_not_like')

@nlu_processing
def get_background_flags(context):
    return