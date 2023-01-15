from chirpy.response_generators.celeb import celeb_helper
from chirpy.core.response_generator.nlu import nlu_processing

@nlu_processing
def get_flags(context):
    ADD_NLU_FLAG('CELEB__known_work')
    return