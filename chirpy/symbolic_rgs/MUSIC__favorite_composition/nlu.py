from chirpy.core.response_generator.nlu import nlu_processing
from chirpy.databases.databases import exists
from chirpy.response_generators.music.regex_templates.name_favorite_composition_template import NameFavoriteCompositionTemplate

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
    composition_entity = get_composition_entity(context)
    ADD_NLU_FLAG('MUSIC__fav_composition_ent', composition_entity)

    composition_str = None
    slots = NameFavoriteCompositionTemplate().execute(context.utterance)
    if slots is not None and 'favorite' in slots:
        composition_str = slots['favorite']

    if composition_entity:
        ADD_NLU_FLAG('MUSIC__fav_composition_str_exists')
        ADD_NLU_FLAG('MUSIC__fav_composition_str', composition_entity.name)
    elif composition_str:
        ADD_NLU_FLAG('MUSIC__fav_composition_str_exists')
        ADD_NLU_FLAG('MUSIC__fav_composition_str', composition_str.capitalize())

@nlu_processing
def get_background_flags(context):
    return


