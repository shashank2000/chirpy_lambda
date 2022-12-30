from chirpy.core.response_generator.response_type import add_response_types, ResponseType
from chirpy.response_generators.movie.expression_lists import YES, NO

import logging
import re
logger = logging.getLogger('chirpylogger')


def found_phrase(phrase, utterance):
    return re.search(f'(\A| ){phrase}(\Z| )', utterance) is not None


def is_positive(rg, utterance):
    top_da = rg.state_manager.current_state.dialogact['top_1']
    return top_da == 'pos_answer' or \
        utterance.lower() in YES or \
        (any(found_phrase(i.lower(), utterance) for i in YES) and not any(found_phrase(i.lower(), utterance) for i in NO))