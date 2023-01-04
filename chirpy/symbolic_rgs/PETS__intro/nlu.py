from chirpy.core.response_generator.nlu import nlu_processing

@nlu_processing
def get_flags(context):
    ans = context.utterance.lower()
    if "ye" in ans:
        ADD_NLU_FLAG('PETS__userOwnsPet') 
    elif "no" in ans or "nah" in ans:
        ADD_NLU_FLAG('PETS__userOwnsNoPet') 
    


@nlu_processing
def get_background_flags(context):
    return