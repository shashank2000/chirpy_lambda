from chirpy.response_generators.celeb import celeb_helper
from chirpy.core.response_generator.nlu import nlu_processing

@nlu_processing
def get_flags(context):
    ADD_NLU_FLAG('CELEB__visited')
    ADD_NLU_FLAG('CELEB__generic')


@nlu_processing
def get_background_flags(context):
    return