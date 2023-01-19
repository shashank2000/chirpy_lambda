from chirpy.core.response_generator.nlu import nlu_processing
from chirpy.core.regex.word_lists import YES, NO
from chirpy.annotators.corenlp import Sentiment

def substr_search(ans):
    # loop through elements of YES,
    # if ans is a substring of any of them, return true
    # else return false
    for word in YES:
        if word in ans:
            return True
    return False

@nlu_processing
def get_flags(context):
    # this is run before the user has said anything this turn
    ans = context.utterance.lower()
    # view all flags currently set
    if ans in YES or substr_search(ans):
        ADD_NLU_FLAG('PETS__user_owns_pet')
    elif ans in NO:
        ADD_NLU_FLAG('PETS__user_owns_no_pet')
    else:
        ADD_NLU_FLAG('PETS__user_mentioned_pet', False)
        return
    if context.state_manager.current_state.corenlp['sentiment'] in (Sentiment.NEGATIVE, Sentiment.STRONG_NEGATIVE):
        ADD_NLU_FLAG("PETS__move_on_to_new_topic")
    ADD_NLU_FLAG('PETS__user_mentioned_pet', True)





@nlu_processing
def get_background_flags(context):
    return
