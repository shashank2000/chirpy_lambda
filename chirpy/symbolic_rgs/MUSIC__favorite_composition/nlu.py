from chirpy.core.response_generator.nlu import nlu_processing
from chirpy.databases.databases import exists
from chirpy.response_generators.music.regex_templates.name_favorite_composition_template import NameFavoriteCompositionTemplate, NameFavoriteCompositionWithDatabaseTemplate

def get_composition_entity(context):
    def is_in_composition_comment_database(ent):
        return ent and exists("music_composition_comment", ent.name.lower())

    cur_entity = context.utilities["cur_entity"]
    entity_linker_results = context.state_manager.current_state.entity_linker
    entities = []
    if cur_entity: entities.append(cur_entity)
    if len(entity_linker_results.high_prec): entities.append(entity_linker_results.high_prec[0].top_ent)
    if len(entity_linker_results.threshold_removed): entities.append(entity_linker_results.threshold_removed[0].top_ent)
    if len(entity_linker_results.conflict_removed): entities.append(entity_linker_results.conflict_removed[0].top_ent)

    for e in entities:
        if is_in_composition_comment_database(e):
            return e

@nlu_processing
def get_flags(context):
    composition_entity = get_composition_entity(context)
    ADD_NLU_FLAG('MUSIC__fav_composition_ent', composition_entity)

    composition_str = None

    composition_str_database_slot = None
    slots_with_database = NameFavoriteCompositionWithDatabaseTemplate().execute(context.utterance.lower())
    if slots_with_database  is not None and 'database_composition' in slots_with_database :
        composition_str_database_slot = slots_with_database['database_composition']

    composition_str_wo_database_slot = None
    slots_wo_database = NameFavoriteCompositionTemplate().execute(context.utterance)
    if slots_wo_database is not None and 'favorite' in slots_wo_database:
        composition_str_wo_database_slot = slots_wo_database['favorite']

    if composition_entity:
        composition_str = composition_entity.name
    elif  composition_str_database_slot:
        composition_str =  composition_str_database_slot.capitalize()
    elif composition_str_wo_database_slot:
        composition_str = composition_str_wo_database_slot.capitalize()

    ADD_NLU_FLAG('MUSIC__fav_composition_str', composition_str)

@nlu_processing
def get_background_flags(context):
    return