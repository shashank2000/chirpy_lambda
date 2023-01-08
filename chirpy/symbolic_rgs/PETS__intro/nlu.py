from chirpy.core.response_generator.nlu import nlu_processing
from chirpy.core.regex.word_lists import YES, NO

@nlu_processing
def get_flags(context):
    # this is run before the user has said anything this turn
    ans = context.utterance.lower()
    # view all flags currently set
    if ans in YES:
        ADD_NLU_FLAG('PETS__user_owns_pet') 
    elif ans in NO:
        ADD_NLU_FLAG('PETS__user_owns_no_pet') 
    else:
        ADD_NLU_FLAG('PETS__user_mentioned_pets', False)
        return
    ADD_NLU_FLAG('PETS__user_mentioned_pets', True)
    

    


@nlu_processing
def get_background_flags(context):
    return