from chirpy.response_generators.food import food_helpers
from chirpy.core.response_generator.nlu import nlu_processing


# check if genre is real
def real_genre(genre):
    return True

@nlu_processing
def get_flags(context):
    entity = context.utilities["cur_entity"]
    if entity is None: return
    
    #entity_name = entity.name.lower()
    if real_genre(entity):
        ADD_NLU_FLAG('MOVIE__user_mentioned_preferred_genre', True)

@nlu_processing
def get_background_flags(context):
    return