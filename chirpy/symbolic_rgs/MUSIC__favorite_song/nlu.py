from chirpy.core.response_generator.nlu import nlu_processing
from chirpy.response_generators.music.utils import WikiEntityInterface
from chirpy.core.entity_linker.entity_groups import ENTITY_GROUPS_FOR_EXPECTED_TYPE
from chirpy.core.entity_linker.entity_linker_simple import link_span_to_entity
from chirpy.response_generators.music.regex_templates.name_favorite_song_template import NameFavoriteSongTemplate, NameFavoriteSongWithDatabaseTemplate
from chirpy.databases.databases import exists
from chirpy.databases.datalib.music_database import music_song_str_wiki
import re

def get_song_entity(context):
    def is_wiki_song(ent):
        return ent and WikiEntityInterface.is_in_entity_group(ent, ENTITY_GROUPS_FOR_EXPECTED_TYPE.musical_work)

    def is_in_song_database(ent):
        return ent and exists("music_song", ent.name.lower())

    cur_entity = context.utilities["cur_entity"]
    entity_linker_results = context.state_manager.current_state.entity_linker
    entities = []
    if cur_entity: entities.append(cur_entity)
    if len(entity_linker_results.high_prec): entities.append(entity_linker_results.high_prec[0].top_ent)
    if len(entity_linker_results.threshold_removed): entities.append(entity_linker_results.threshold_removed[0].top_ent)
    if len(entity_linker_results.conflict_removed): entities.append(entity_linker_results.conflict_removed[0].top_ent)

    for e in entities:
        if is_in_song_database(e):
            return e
    for e in entities:
        if is_wiki_song(e):
            return

def get_song_entity_from_str(context, string):
    return link_span_to_entity(string, context.state_manager.current_state, expected_type=ENTITY_GROUPS_FOR_EXPECTED_TYPE.musical_work)

@nlu_processing
def get_flags(context):
    song_ent = get_song_entity(context)
    song_str = None

    song_str_database_slot = None
    slots_with_database = NameFavoriteSongWithDatabaseTemplate().execute(context.utterance.lower())
    if slots_with_database is not None and 'database_song' in slots_with_database:
        song_str_database_slot = slots_with_database['database_song']

    song_str_wo_database_slot = None
    slots_wo_database = NameFavoriteSongTemplate().execute(context.utterance)
    if slots_wo_database is not None and 'favorite' in slots_wo_database:
        song_str_wo_database_slot = slots_wo_database['favorite']

    if song_ent:
        song_str = song_ent.name
    elif song_str_database_slot:
        song_str = music_song_str_wiki[song_str_database_slot]['wiki_doc_title']
        song_ent = get_song_entity_from_str(context, song_str)
    elif song_str_wo_database_slot:
        song_str = song_str_wo_database_slot.capitalize()

    song_talkable = re.sub(r'\(.*?\)', '', song_str).capitalize() if song_str else None


    ADD_NLU_FLAG('MUSIC__fav_song_ent', song_ent)
    ADD_NLU_FLAG('MUSIC__fav_song_str', song_str)
    ADD_NLU_FLAG('MUSIC__fav_song_talkable', song_talkable)


@nlu_processing
def get_background_flags(context):
    return

