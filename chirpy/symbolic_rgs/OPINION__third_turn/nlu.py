from chirpy.core.response_generator.nlu import nlu_processing

@nlu_processing
def get_flags(context):
    ADD_NLU_FLAG('OPINION__last_said', context.utterance)

@nlu_processing
def get_background_flags(context):
    pass