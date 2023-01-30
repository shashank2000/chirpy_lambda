from chirpy.core.response_generator.nlu import nlu_processing

from collections import OrderedDict
from chirpy.response_generators.music.regex_templates.word_lists import KEYWORD_MUSIC, FREQUENCY_ANSWERS
from chirpy.response_generators.wiki2.wiki_helpers import is_opinion as is_wiki_opinion
from chirpy.response_generators.music.expression_lists import POSITIVE_WORDS, NEGATIVE_WORDS, PositiveTemplate, NegativeTemplate

import re

# Retrieved tags from MusicBrainz, ordered by popularity
tags = OrderedDict({
    "rock": "rock",
    "electronic": "electronic",
    "pop": "pop",
    "jazz": "jazz",
    "punk": "punk",
    "techno": "techno",
    "classical": "classical",
    "hip-hop": "hip-hop",
    "alternative rock": "alternative rock",
    "blues": "blues",
    "experimental": "experimental",
    "folk": "folk",
    "country": "country",
    "electro": "electro",
    "downtempo": "downtempo",
    "hard rock": "hard rock",
    "alternative": "alternative",
    "metal": "metal",
    "r b": "r & b",
    "christmas": "christmas",
    "alternative and punk": "alternative and punk",
    "synth-pop": "synth-pop",
    "indie": "indie",
    "soul": "blues",
    "indie rock": "indie rock",
    "hip hop rap": "hip hop rap",
    "idm": "IDM",
    "pop rock": "pop rock",
    "heavy metal": "heavy metal",
    "hip hop": "hip hop",
    "progressive rock": "progressive rock",
    "disco": "disco",
    "tech house": "tech house",
    "reggae": "reggae",
    "folk rock": "folk rock",
    "rap": "rap",
    "new wave": "new wave",
    "classic rock": "classic rock",
    "punk rock": "punk rock",
    "electronica dance": "electronica dance",
    "breakbeat": "breakbeat",
    "rock pop": "rock pop",
    "dance": "dance",
    "american": "american",
    "psychedelic rock": "psychedelic rock",
    "funk": "funk",
    "classic pop and rock": "classic pop and rock",
    "rock and indie": "rock and indie",
    "leftfield": "leftfield",
    "ska": "ska",
    "death metal": "death metal",
    "funk soul": "funk soul",
    "comedy": "comedy",
    "instrumental": "instrumental",
    "euro house": "euro house",
    "french": "french",
    "progressive house": "progressive house",
    "electronica": "electronica",
    "acoustic": "acoustic",
    "alternative punk": "alternative punk",
    "ebm": "EBM",
    "grunge": "grunge",
    "soft rock": "soft rock",
    "new age": "new age",
    "trip hop": "trip hop",
    "disco eurobeat": "disco eurobeat",
    "black metal": "black metal",
    "future jazz": "future jazz",
})

def found_phrase(phrase, utterance):
    return re.search(f'(\A| ){phrase}[\.!]?(\Z| )', utterance) is not None

def is_music_keyword(context):
    return any(found_phrase(i, context.utterance) for i in KEYWORD_MUSIC)

def is_freq_answer(context):
    return any(found_phrase(i, context.utterance) for i in FREQUENCY_ANSWERS)

def is_music_response(context):
    return any(found_phrase(i, context.utterance) for i in tags.keys())

def is_opinion(context):
    return len(context.utterance.split()) >= 10 or is_wiki_opinion(context)

def is_positive(context):
    top_da = context.state_manager.current_state.dialogact['top_1']
    return top_da == 'pos_answer' or \
    (any(found_phrase(i, context.utterance) for i in POSITIVE_WORDS) and not any(found_phrase(i, context.utterance) for i in NEGATIVE_WORDS))

def is_negative(context):
    top_da = context.state_manager.current_state.dialogact['top_1']
    return top_da == 'neg_answer' or any(found_phrase(i, context.utterance) for i in NEGATIVE_WORDS)


@nlu_processing
def get_flags(context):
    if is_freq_answer(context):
        ADD_NLU_FLAG('MUSIC__user_listens_frequently')
        if 'everyday' in context.utterance:
            ADD_NLU_FLAG('MUSIC__user_listens_everyday')
    if is_negative(context):
        ADD_NLU_FLAG('MUSIC__user_has_negative_response')
    elif is_positive(context):
        ADD_NLU_FLAG('MUSIC__user_has_positive_response')
    if is_music_response(context):
        ADD_NLU_FLAG('MUSIC__user_response_is_music_response')


@nlu_processing
def get_background_flags(context):
    return