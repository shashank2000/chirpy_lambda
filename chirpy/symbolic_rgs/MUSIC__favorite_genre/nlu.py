from chirpy.core.response_generator.nlu import nlu_processing

from chirpy.response_generators.music.utils import WikiEntityInterface
from chirpy.core.entity_linker.entity_groups import ENTITY_GROUPS_FOR_EXPECTED_TYPE
from chirpy.symbolic_rgs.MUSIC__intro.nlu import tags, found_phrase
from chirpy.core.util import query_es_index, get_es_host, get_elasticsearch

def get_genre_entity(context):
    def is_genre(ent):
        return ent and WikiEntityInterface.is_in_entity_group(ent, ENTITY_GROUPS_FOR_EXPECTED_TYPE.music_genre)

    cur_entity = context.utilities["cur_entity"]
    entity_linker_results = context.state_manager.current_state.entity_linker
    entities = []
    if cur_entity: entities.append(cur_entity)
    if len(entity_linker_results.high_prec): entities.append(entity_linker_results.high_prec[0].top_ent)
    if len(entity_linker_results.threshold_removed): entities.append(entity_linker_results.threshold_removed[0].top_ent)
    if len(entity_linker_results.conflict_removed): entities.append(entity_linker_results.conflict_removed[0].top_ent)

    genre = None
    for e in entities:
        if is_genre(e) and genre is None:
            genre = e

    return genre

@nlu_processing
def get_flags(context):
    genre_ent = get_genre_entity(context)
    genre_str = None
    if genre_ent:
        genre_str = genre_ent.talkable_name[:-6] if genre_ent.talkable_name.endswith('music') else genre_ent.talkable_name

    ADD_NLU_FLAG('MUSIC__fav_genre', genre_ent)
    ADD_NLU_FLAG('MUSIC__fav_genre_str', genre_str)

    if genre_str and genre_str.lower() == 'classical':
        ADD_NLU_FLAG('MUSIC__fav_genre_work_descriptor', 'piece')
    else:
        ADD_NLU_FLAG('MUSIC__fav_genre_work_descriptor', 'song')

@nlu_processing
def get_background_flags(context):
    return
