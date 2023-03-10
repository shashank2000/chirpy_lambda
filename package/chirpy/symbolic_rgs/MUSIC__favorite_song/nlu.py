from chirpy.core.response_generator.nlu import nlu_processing
from chirpy.response_generators.music.utils import WikiEntityInterface
from chirpy.core.entity_linker.entity_groups import ENTITY_GROUPS_FOR_EXPECTED_TYPE
from chirpy.databases.databases import exists, lookup
from chirpy.core.entity_linker.entity_linker_simple import get_entity_by_wiki_name
from chirpy.databases.datalib.music_database import music_song_str_wiki
from chirpy.response_generators.music.regex_templates.name_favorite_song_template import NameFavoriteSongTemplate, NameFavoriteSongWithDatabaseTemplate
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

@nlu_processing
def get_flags(context):
    # Find entity with database
    song_str_database_slot = None
    slots_with_database = NameFavoriteSongWithDatabaseTemplate().execute(context.utterance.lower())
    if slots_with_database is not None and 'database_song' in slots_with_database:
        song_str_database_slot = slots_with_database['database_song']

    # Find entity with entity linker
    song_ent = get_song_entity(context)


    # Find str with slot
    song_str_wo_database_slot = None
    slots_wo_database = NameFavoriteSongTemplate().execute(context.utterance)
    if slots_wo_database is not None and 'favorite' in slots_wo_database:
        song_str_wo_database_slot = slots_wo_database['favorite']

    song_str = None
    song_talkable = None

    if song_str_database_slot:
        if song_str_database_slot in music_song_str_wiki:
            song_str = lookup("music_song_str_wiki", song_str_database_slot)['database_key']
        else:
            song_str = song_str_database_slot
        song_wiki_doc_title = lookup("music_song", song_str)['wiki_doc_title']
        song_ent = get_entity_by_wiki_name(song_wiki_doc_title)
        song_talkable = song_wiki_doc_title
    elif song_ent:
        song_str = song_ent.name
        song_talkable = song_str
    elif song_str_wo_database_slot:
        song_str = song_str_wo_database_slot
        song_talkable = re.sub('(^| |\.)(.)', lambda x: x.group().upper(), song_str)

    song_talkable = re.sub(r'\(.*?\)', '', song_talkable).strip() if song_talkable else None

    ADD_NLU_FLAG('MUSIC__fav_song_ent', song_ent)
    ADD_NLU_FLAG('MUSIC__fav_song_str', song_str)
    ADD_NLU_FLAG('MUSIC__fav_song_talkable', song_talkable)

@nlu_processing
def get_background_flags(context):
    return

