from chirpy.core.response_generator.nlu import nlu_processing
from chirpy.response_generators.music.utils import WikiEntityInterface
from chirpy.databases.databases import exists
from chirpy.core.entity_linker.entity_groups import ENTITY_GROUPS_FOR_EXPECTED_TYPE

def get_instrument_entity(context):
    def is_wiki_instrument(ent):
        return ent and WikiEntityInterface.is_in_entity_group(ent, ENTITY_GROUPS_FOR_EXPECTED_TYPE.musical_instrument)
    def is_in_instrument_database(ent):
        return ent and exists("music_instrument", ent.name.lower())

    cur_entity = context.utilities["cur_entity"]
    entity_linker_results = context.state_manager.current_state.entity_linker
    entities = []
    if cur_entity: entities.append(cur_entity)
    if len(entity_linker_results.high_prec): entities.append(entity_linker_results.high_prec[0].top_ent)
    if len(entity_linker_results.threshold_removed): entities.append(entity_linker_results.threshold_removed[0].top_ent)
    if len(entity_linker_results.conflict_removed): entities.append(entity_linker_results.conflict_removed[0].top_ent)

    for e in entities:
        if is_in_instrument_database(e):
            return e

    for e in entities:
        if is_wiki_instrument(e):
            return e

@nlu_processing
def get_flags(context):
    instr_entity = get_instrument_entity(context)
    instr_str = None
    ADD_NLU_FLAG('MUSIC__instr_to_learn_ent', instr_entity)
    if instr_entity:
        instr_str = instr_entity.name
    elif exists("music_instrument", context.utterance.lower()):
        instr_str = context.utterance

    ADD_NLU_FLAG('MUSIC__instr_to_learn_str', instr_str)


@nlu_processing
def get_background_flags(context):
    return