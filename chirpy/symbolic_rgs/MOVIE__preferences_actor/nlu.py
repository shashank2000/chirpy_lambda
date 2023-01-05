from chirpy.response_generators.food import food_helpers
from chirpy.core.response_generator.nlu import nlu_processing


# check if move is True
def real_actor(actor):
    return True

@nlu_processing
def get_flags(context):
    entity = context.utilities["cur_entity"]
    if entity is None: return
    
    #entity_name = entity.name.lower()
    if real_actor(entity):
        ADD_NLU_FLAG('MOVIE__user_mentioned_preferred_actor', True)

@nlu_processing
def get_background_flags(context):
    return