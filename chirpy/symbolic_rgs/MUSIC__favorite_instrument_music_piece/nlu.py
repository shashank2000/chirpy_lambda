from chirpy.core.response_generator.nlu import nlu_processing
import re


def found_phrase(phrase, utterance):
    return re.search(f'(\A| ){phrase}(\Z| )', utterance) is not None


@nlu_processing
def get_flags(context):
    if found_phrase('years', context.utterance):
        ADD_NLU_FLAG('MUSIC__advanced_musician')

@nlu_processing
def get_background_flags(context):
    return


