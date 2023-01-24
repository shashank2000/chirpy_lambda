from chirpy.core.response_generator.nlu import nlu_processing
from chirpy.core.entity_linker.entity_groups import EntityGroupsForExpectedType


@nlu_processing
def get_flags(context):
    entity = context.utilities["cur_entity"]
    if entity is None: 
        return
    if EntityGroupsForExpectedType.film.matches(entity):
        ADD_NLU_FLAG('MOVIE__user_mentioned_movie', True)


@nlu_processing
def get_background_flags(context):
    return
