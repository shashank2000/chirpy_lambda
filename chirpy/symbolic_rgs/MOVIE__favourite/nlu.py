from chirpy.response_generators.food import food_helpers
from chirpy.core.response_generator.nlu import nlu_processing


# check if movie is True
def real_movie(movie):
    return True


@nlu_processing
def get_flags(context):
    entity = context.utilities["cur_entity"]
    if entity is None: 
        return
    if real_movie(entity):
        ADD_NLU_FLAG('MOVIE__user_mentioned_movie', True)


@nlu_processing
def get_background_flags(context):
    return
