from chirpy.core.response_generator.nlu import nlu_processing
from chirpy.core.regex.word_lists import YES

@nlu_processing
def get_flags(context):
    # this is run before the user has said anything this turn
    ans = context.utterance.lower()
    # view all flags currently set
    if ans in YES:
        ADD_NLU_FLAG('PETS__user_owns_pet') 
    else:
        ADD_NLU_FLAG('PETS__user_owns_no_pet') 
    


@nlu_processing
def get_background_flags(context):
    return