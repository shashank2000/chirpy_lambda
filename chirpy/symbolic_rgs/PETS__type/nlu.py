from chirpy.core.response_generator.nlu import nlu_processing

@nlu_processing
def get_flags(context):
    ans = context.utterance.lower()
    #ADD_NLU_FLAG('PET__favoritePetType', ans) 

    


@nlu_processing
def get_background_flags(context):
    return