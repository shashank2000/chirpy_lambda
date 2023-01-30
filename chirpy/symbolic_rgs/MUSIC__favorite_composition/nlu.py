from chirpy.core.response_generator.nlu import nlu_processing
from chirpy.databases.databases import exists, lookup
from chirpy.core.entity_linker.entity_linker_simple import get_entity_by_wiki_name
from chirpy.response_generators.music.regex_templates.name_favorite_composition_template import NameFavoriteCompositionTemplate, NameFavoriteCompositionWithDatabaseTemplate
import re

def get_composition_entity(context):
    def is_in_composition_database(ent):
        return ent and exists("music_composition", ent.name.lower())

    cur_entity = context.utilities["cur_entity"]
    entity_linker_results = context.state_manager.current_state.entity_linker
    entities = []
    if cur_entity: entities.append(cur_entity)
    if len(entity_linker_results.high_prec): entities.append(entity_linker_results.high_prec[0].top_ent)
    if len(entity_linker_results.threshold_removed): entities.append(entity_linker_results.threshold_removed[0].top_ent)
    if len(entity_linker_results.conflict_removed): entities.append(entity_linker_results.conflict_removed[0].top_ent)

    for e in entities:
        if is_in_composition_database(e):
            return e

@nlu_processing
def get_flags(context):
    # Find entity with database
    composition_str_database_slot = None
    slots_with_database = NameFavoriteCompositionWithDatabaseTemplate().execute(context.utterance.lower())
    if slots_with_database is not None and 'database_composition' in slots_with_database :
        composition_str_database_slot = slots_with_database['database_composition']

    # Find entity with entity linker
    composition_ent = get_composition_entity(context)
    composition_str = None

    # Find str with slot
    composition_str_wo_database_slot = None
    slots_wo_database = NameFavoriteCompositionTemplate().execute(context.utterance)
    if slots_wo_database is not None and 'favorite' in slots_wo_database:
        composition_str_wo_database_slot = slots_wo_database['favorite']

    if composition_str_database_slot:
        if exists("music_composition_str_wiki", composition_str_database_slot):
            composition_str = lookup("music_composition_str_wiki", composition_str_database_slot)['database_key']
        else:
            composition_str = composition_str_database_slot
        composition_wiki_doc_title = lookup("music_composition", composition_str)['wiki_doc_title']
        composition_ent = get_entity_by_wiki_name(composition_wiki_doc_title)
    elif composition_ent:
        composition_str = composition_ent.name
    elif composition_str_wo_database_slot:
        composition_str = composition_str_wo_database_slot

    composition_talkable = re.sub(r'\(.*?\)', '', composition_str.lower()).strip() if composition_str else None
    composition_talkable = re.sub('(^| |\.)(.)', lambda x: x.group().upper(), composition_talkable) if composition_talkable else None

    ADD_NLU_FLAG('MUSIC__fav_composition_ent', composition_ent)
    ADD_NLU_FLAG('MUSIC__fav_composition_str', composition_str)
    ADD_NLU_FLAG('MUSIC__fav_composition_talkable', composition_talkable)

@nlu_processing
def get_background_flags(context):
    return