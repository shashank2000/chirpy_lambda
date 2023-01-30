from chirpy.core.response_generator.nlu import nlu_processing
from chirpy.response_generators.music.utils import WikiEntityInterface
from chirpy.core.entity_linker.entity_groups import ENTITY_GROUPS_FOR_EXPECTED_TYPE
from chirpy.response_generators.music.regex_templates.name_favorite_instrument_template import NameInstrumentWithDatabaseTemplate
from chirpy.databases.databases import exists, lookup
from chirpy.core.entity_linker.entity_linker_simple import get_entity_by_wiki_name
import re

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
    # Find entity with database
    instr_str_database_slot = None
    slots_with_database = NameInstrumentWithDatabaseTemplate().execute(context.utterance.lower())
    if slots_with_database is not None and 'database_instr' in slots_with_database:
        instr_str_database_slot = slots_with_database['database_instr']

    # Find entity with entity linker
    instr_str = None
    instr_ent = get_instrument_entity(context)

    if instr_str_database_slot:
        instr_str = instr_str_database_slot
        instr_wiki_doc_title = lookup("music_instrument", instr_str)['wiki_doc_title']
        instr_ent = get_entity_by_wiki_name(instr_wiki_doc_title)
    elif instr_ent:
        instr_str = instr_ent.name

    instr_talkable = re.sub(r'\(.*?\)', '', instr_str.lower()).strip() if instr_str else None
    instr_talkable = re.sub('(^| |\.)(.)', lambda x: x.group().upper(), instr_talkable) if instr_talkable else None

    ADD_NLU_FLAG('MUSIC__instr_to_learn_ent', instr_ent)
    ADD_NLU_FLAG('MUSIC__instr_to_learn_str', instr_str)
    ADD_NLU_FLAG('MUSIC__instr_to_learn_talkable', instr_talkable)

@nlu_processing
def get_background_flags(context):
    return