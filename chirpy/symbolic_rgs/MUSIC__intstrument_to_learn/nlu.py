from chirpy.core.response_generator.nlu import nlu_processing
from chirpy.response_generators.music.utils import WikiEntityInterface
from chirpy.core.entity_linker.entity_groups import ENTITY_GROUPS_FOR_EXPECTED_TYPE
from chirpy.response_generators.wiki2.wiki_utils import get_til_title

def get_instrument_entity(context):
    def is_instrument(ent):
        return ent and WikiEntityInterface.is_in_entity_group(ent, ENTITY_GROUPS_FOR_EXPECTED_TYPE.musical_instrument)

    cur_entity = context.utilities["cur_entity"]
    entity_linker_results = context.state_manager.current_state.entity_linker
    entities = []
    if cur_entity: entities.append(cur_entity)
    if len(entity_linker_results.high_prec): entities.append(entity_linker_results.high_prec[0].top_ent)
    if len(entity_linker_results.threshold_removed): entities.append(entity_linker_results.threshold_removed[0].top_ent)
    if len(entity_linker_results.conflict_removed): entities.append(entity_linker_results.conflict_removed[0].top_ent)

    for e in entities:
        if is_instrument(e):
            print(e)
            return e

@nlu_processing
def get_flags(context):
    instr_entity = get_instrument_entity(context)
    ADD_NLU_FLAG('MUSIC__instrument_to_learn_ent', instr_entity)
    if instr_entity:
        tils = get_til_title(instr_entity.name)
        if len(tils):
            ADD_NLU_FLAG('MUSIC__instr_to_learn_exists_with_til')
        else:
            ADD_NLU_FLAG('MUSIC__instr_to_learn_exists_wo_til')

@nlu_processing
def get_background_flags(context):
    return


