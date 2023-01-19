from chirpy.response_generators.wiki2 import wiki_helpers
from chirpy.core.response_generator.nlu import nlu_processing
from chirpy.core.camel.context import Context

@nlu_processing
def get_flags(context):
    wiki_helpers.add_flags(context, ADD_NLU_FLAG)

@nlu_processing
def get_background_flags(context):
    return