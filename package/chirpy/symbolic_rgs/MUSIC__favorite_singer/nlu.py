from chirpy.core.response_generator.nlu import nlu_processing

from chirpy.core.entity_linker.entity_groups import ENTITY_GROUPS_FOR_EXPECTED_TYPE
from chirpy.response_generators.music.utils import WikiEntityInterface
from chirpy.core.entity_linker.entity_linker_simple import link_span_to_entity
import chirpy.response_generators.music.response_templates.general_templates as templates
from chirpy.core.util import choose_least_repetitive
from chirpy.databases.databases import exists, lookup
from chirpy.core.entity_linker.entity_linker_simple import get_entity_by_wiki_name
from chirpy.databases.datalib.music_database import music_singer_str_wiki
from chirpy.response_generators.music.regex_templates.name_favorite_singer_template import NameFavoriteSingerTemplate, NameFavoriteSingerWithDatabaseTemplate

import re
from chirpy.response_generators.music.expression_lists import NEGATIVE_WORDS

def get_singer_entity(context):
    def is_wiki_singer(ent):
        return ent and WikiEntityInterface.is_in_entity_group(ent, ENTITY_GROUPS_FOR_EXPECTED_TYPE.musician)
    def is_in_singer_database(ent):
        return ent and exists("music_singer", ent.name.lower())

    cur_entity = context.utilities["cur_entity"]
    entity_linker_results = context.state_manager.current_state.entity_linker
    entities = []
    if cur_entity: entities.append(cur_entity)
    if len(entity_linker_results.high_prec): entities.append(entity_linker_results.high_prec[0].top_ent)
    if len(entity_linker_results.threshold_removed): entities.append(entity_linker_results.threshold_removed[0].top_ent)
    if len(entity_linker_results.conflict_removed): entities.append(entity_linker_results.conflict_removed[0].top_ent)

    for e in entities:
        if is_in_singer_database(e):
            return e

    for e in entities:
        if is_wiki_singer(e):
            return e

def get_singer_entity_from_str(context, string):
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
    # Find entity with database
    singer_str_database_slot = None
    slots_with_database = NameFavoriteSingerWithDatabaseTemplate().execute(context.utterance.lower())
    if slots_with_database is not None and 'database_singer' in slots_with_database:
        singer_str_database_slot = slots_with_database['database_singer']

    # Find entity with entity linker
    singer_ent = get_singer_entity(context)

    # Find str with slot
    singer_str_wo_database_slot = None
    slots_wo_database = NameFavoriteSingerTemplate().execute(context.utterance)
    if slots_wo_database is not None and 'favorite' in slots_wo_database:
        singer_str_wo_database_slot = slots_wo_database['favorite']

    singer_str = None
    singer_talkable = None

    if singer_str_database_slot:
        if singer_str_database_slot in music_singer_str_wiki:
            singer_str = lookup("music_singer_str_wiki", singer_str_database_slot)['database_key']
        else:
            singer_str = singer_str_database_slot
        singer_wiki_doc_title = lookup("music_singer", singer_str)['wiki_doc_title']
        singer_ent = get_entity_by_wiki_name(singer_wiki_doc_title)
        singer_talkable = singer_wiki_doc_title
    elif singer_ent:
        singer_str = singer_ent.name
        singer_talkable = singer_str
    elif singer_str_wo_database_slot:
        singer_str = singer_str_wo_database_slot
        singer_talkable = re.sub('(^| |\.)(.)', lambda x: x.group().upper(), singer_str)


    singer_talkable = re.sub(r'\(.*?\)', '', singer_talkable).strip() if singer_talkable else None

    ADD_NLU_FLAG('MUSIC__fav_singer_ent', singer_ent)
    ADD_NLU_FLAG('MUSIC__fav_singer_str', singer_str)
    ADD_NLU_FLAG('MUSIC__fav_singer_talkable', singer_talkable)

    if singer_ent:
        if WikiEntityInterface.is_in_entity_group(singer_ent, ENTITY_GROUPS_FOR_EXPECTED_TYPE.musical_group):
            ADD_NLU_FLAG('MUSIC__singer_is_musical_group')

    if is_negative(context):
        ADD_NLU_FLAG('MUSIC__user_has_negative_response')

    ADD_NLU_FLAG('MUSIC__fav_singer_comment', least_repetitive_compliment(context))

@nlu_processing
def get_background_flags(context):
    return