from chirpy.core.response_generator.nlu import nlu_processing

from chirpy.core.entity_linker.entity_groups import ENTITY_GROUPS_FOR_EXPECTED_TYPE
from chirpy.response_generators.music.utils import WikiEntityInterface
from chirpy.core.entity_linker.entity_linker_simple import link_span_to_entity
from chirpy.response_generators.music.regex_templates import NameFavoriteSongTemplate

import chirpy.response_generators.music.response_templates.general_templates as templates
from chirpy.core.util import choose_least_repetitive

import re
from chirpy.response_generators.music.expression_lists import NEGATIVE_WORDS

def get_singer_entity(context):
    def is_singer(ent):
        return ent and WikiEntityInterface.is_in_entity_group(ent, ENTITY_GROUPS_FOR_EXPECTED_TYPE.musician)

    cur_entity = context.utilities["cur_entity"]
    entity_linker_results = context.state_manager.current_state.entity_linker
    entities = []
    if cur_entity: entities.append(cur_entity)
    if len(entity_linker_results.high_prec): entities.append(entity_linker_results.high_prec[0].top_ent)
    if len(entity_linker_results.threshold_removed): entities.append(entity_linker_results.threshold_removed[0].top_ent)
    if len(entity_linker_results.conflict_removed): entities.append(entity_linker_results.conflict_removed[0].top_ent)
    print(f'0: {entities}')
    for e in entities:
        if is_singer(e): return e

def get_musician_entity(context, string):
    return link_span_to_entity(string, context.state_manager.current_state, expected_type=ENTITY_GROUPS_FOR_EXPECTED_TYPE.musician)

def found_phrase(phrase, utterance):
    return re.search(f'(\A| ){phrase}(\Z| )', utterance) is not None

def is_negative(context):
    top_da = context.state_manager.current_state.dialogact['top_1']
    return top_da == 'neg_answer' or any(found_phrase(i, context.utterance) for i in NEGATIVE_WORDS)

def least_repetitive_compliment(context):
    return choose_least_repetitive(context, templates.compliment_user_musician_choice())

@nlu_processing
def get_flags(context):
    singer_ent = get_singer_entity(context)
    singer_str = None if singer_ent is None else re.sub(r'\(.*?\)', '', singer_ent.talkable_name)

    if singer_ent is None:
        slots = NameFavoriteSongTemplate().execute(context.utterance)
        if slots is not None and 'favorite' in slots:
            singer_str = slots['favorite']
            singer_ent = get_musician_entity(context, singer_str)
            if singer_ent:
                singer_str = singer_ent.name

    ADD_NLU_FLAG('MUSIC__fav_singer_ent', singer_ent)
    ADD_NLU_FLAG('MUSIC__fav_singer_str', singer_str)

    if singer_ent:
        if WikiEntityInterface.is_in_entity_group(singer_ent, ENTITY_GROUPS_FOR_EXPECTED_TYPE.musical_group):
            ADD_NLU_FLAG('MUSIC__singer_is_musical_group')

    if is_negative(context):
        ADD_NLU_FLAG('MUSIC__user_has_negative_response')

    ADD_NLU_FLAG('MUSIC__fav_singer_comment', least_repetitive_compliment(context))

@nlu_processing
def get_background_flags(context):
    return

