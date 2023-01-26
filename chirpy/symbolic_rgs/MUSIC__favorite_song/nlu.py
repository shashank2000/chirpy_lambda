from chirpy.core.response_generator.nlu import nlu_processing
from chirpy.response_generators.music.utils import WikiEntityInterface
from chirpy.core.entity_linker.entity_groups import ENTITY_GROUPS_FOR_EXPECTED_TYPE
from chirpy.core.entity_linker.entity_linker_simple import link_span_to_entity
from chirpy.response_generators.music.regex_templates import NameFavoriteSongTemplate
import re

def get_song_and_singer_entity(context):
    def is_song(ent):
        return ent and WikiEntityInterface.is_in_entity_group(ent, ENTITY_GROUPS_FOR_EXPECTED_TYPE.musical_work)

    def is_singer(ent):
        return ent and WikiEntityInterface.is_in_entity_group(ent, ENTITY_GROUPS_FOR_EXPECTED_TYPE.musician)

    cur_entity = context.utilities["cur_entity"]
    entity_linker_results = context.state_manager.current_state.entity_linker
    song, singer = None, None
    entities = []
    if cur_entity: entities.append(cur_entity)
    if len(entity_linker_results.high_prec): entities.append(entity_linker_results.high_prec[0].top_ent)
    if len(entity_linker_results.threshold_removed): entities.append(entity_linker_results.threshold_removed[0].top_ent)
    if len(entity_linker_results.conflict_removed): entities.append(entity_linker_results.conflict_removed[0].top_ent)

    for e in entities:
        if is_song(e) and song is None:
            song = e
        elif is_singer(e) and singer is None:
            singer = e
    return song, singer

def get_song_entity(context, string):
    return link_span_to_entity(string, context.state_manager.current_state, expected_type=ENTITY_GROUPS_FOR_EXPECTED_TYPE.musical_work)

@nlu_processing
def get_flags(context):
    song_ent, singer_ent = get_song_and_singer_entity(context)
    song_str = None

    if song_ent:
        song_str = song_ent.talkable_name
        song_str = re.sub(r'\(.*?\)', '', song_str)
    else:
        song_slots = NameFavoriteSongTemplate().execute(context.utterance)
        if song_slots is not None and 'favorite' in song_slots:
            song_str = song_slots['favorite']
            song_ent = get_song_entity(context, song_str)


    ADD_NLU_FLAG('MUSIC__fav_song_ent', song_ent)
    ADD_NLU_FLAG('MUSIC__fav_song_str', song_str)

@nlu_processing
def get_background_flags(context):
    return

