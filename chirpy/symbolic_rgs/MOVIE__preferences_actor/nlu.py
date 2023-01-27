from chirpy.core.response_generator.nlu import nlu_processing
from chirpy.core.entity_linker.entity_groups import EntityGroupsForExpectedType


@nlu_processing
def get_flags(context):
    entity = context.utilities["cur_entity"]
    if entity is None: return
    
    #entity_name = entity.name.lower()
    if EntityGroupsForExpectedType.actor.matches(entity):
        ADD_NLU_FLAG('MOVIE__user_mentioned_preferred_actor', True)


@nlu_processing
def get_background_flags(context):
    return