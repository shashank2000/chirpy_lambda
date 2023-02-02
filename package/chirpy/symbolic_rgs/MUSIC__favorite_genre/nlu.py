from chirpy.core.response_generator.nlu import nlu_processing
from chirpy.response_generators.music.utils import WikiEntityInterface
from chirpy.core.entity_linker.entity_groups import ENTITY_GROUPS_FOR_EXPECTED_TYPE
from chirpy.databases.databases import exists, lookup
from chirpy.core.entity_linker.entity_linker_simple import get_entity_by_wiki_name
from chirpy.response_generators.music.regex_templates.name_favorite_genre_template import NameFavoriteGenreWithDatabaseTemplate, NameFavoriteGenreAbbrevWithDatabaseTemplate
import re

def get_genre_entity(context):
    def is_wiki_genre(ent):
        return ent and WikiEntityInterface.is_in_entity_group(ent, ENTITY_GROUPS_FOR_EXPECTED_TYPE.music_genre)
    def is_in_genre_database(ent):
        return ent and exists("music_genre", ent.name.lower())

    cur_entity = context.utilities["cur_entity"]
    entity_linker_results = context.state_manager.current_state.entity_linker
    entities = []
    if cur_entity: entities.append(cur_entity)
    if len(entity_linker_results.high_prec): entities.append(entity_linker_results.high_prec[0].top_ent)
    if len(entity_linker_results.threshold_removed): entities.append(entity_linker_results.threshold_removed[0].top_ent)
    if len(entity_linker_results.conflict_removed): entities.append(entity_linker_results.conflict_removed[0].top_ent)

    for e in entities:
        if is_in_genre_database(e):
            return e
    for e in entities:
        if is_wiki_genre(e):
            return e

@nlu_processing
def get_flags(context):
    # Find entity with full_name database
    genre_str_database_slot = None
    slots_with_database = NameFavoriteGenreWithDatabaseTemplate().execute(context.utterance.lower())
    if slots_with_database is not None and 'database_genre' in slots_with_database:
        genre_str_database_slot = slots_with_database['database_genre']

    # Find entity with abbrev database
    genre_abbrev_str_database_slot = None
    slots_abbrev_with_database = NameFavoriteGenreAbbrevWithDatabaseTemplate().execute(context.utterance.lower())
    if slots_abbrev_with_database is not None and 'database_genre' in slots_abbrev_with_database:
        genre_abbrev_str_database_slot = slots_abbrev_with_database['database_genre']

    # Find entity with entity linker
    genre_ent = get_genre_entity(context)
    genre_str = None

    if genre_str_database_slot:
        genre_str = genre_str_database_slot
        genre_wiki_doc_title = lookup("music_genre", genre_str)['wiki_doc_title']
        genre_ent = get_entity_by_wiki_name(genre_wiki_doc_title)
    elif genre_abbrev_str_database_slot:
        genre_str = lookup("music_genre_str_wiki", genre_abbrev_str_database_slot)['database_key']
        genre_wiki_doc_title = lookup("music_genre", genre_str)['wiki_doc_title']
        genre_ent = get_entity_by_wiki_name(genre_wiki_doc_title)
    elif genre_ent:
        genre_str = genre_ent.name

    genre_talkable = re.sub(r'\(.*?\)', '', genre_str.lower()).strip() if genre_str else None
    genre_talkable = re.sub('(^| |\.)(.)', lambda x: x.group().upper(), genre_talkable) if genre_talkable else None

    ADD_NLU_FLAG('MUSIC__fav_genre', genre_ent)
    ADD_NLU_FLAG('MUSIC__fav_genre_str', genre_str)
    ADD_NLU_FLAG('MUSIC__fav_genre_talkable', genre_talkable)

    if genre_str:
        modified_genre_str = genre_str[:-6] if genre_str.endswith('music') else genre_str
        if modified_genre_str and modified_genre_str.lower() == 'classical':
            ADD_NLU_FLAG('MUSIC__fav_genre_work_descriptor', 'piece')
        else:
            ADD_NLU_FLAG('MUSIC__fav_genre_work_descriptor', 'song')

@nlu_processing
def get_background_flags(context):
    return