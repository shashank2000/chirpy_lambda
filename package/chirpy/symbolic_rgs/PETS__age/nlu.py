from chirpy.core.response_generator.nlu import nlu_processing

import re

# TODO: add more nlu logic to get age, currrently only gets first number (requires digits in string)
def get_age_from_utterrance(context):
    utterance = context.utterance.lower()
    age = re.search(r'\d+', utterance)
    if age:
        return age.group()
    return None


@nlu_processing
def get_flags(context):
    age = get_age_from_utterrance(context)
    ADD_NLU_FLAG("PETS__age", age)