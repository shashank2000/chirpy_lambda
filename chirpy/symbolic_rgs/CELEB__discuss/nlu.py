from chirpy.response_generators.celeb import celeb_helper
from chirpy.core.response_generator.nlu import nlu_processing

@nlu_processing
def get_flags(context):
    # entity = context.utilities["cur_entity"]
    # if entity is None: return
    #
    # entity_name = entity.name.lower()
    # is_known_celeb = celeb_helper.is_known_celeb(entity_name)
    # if is_known_celeb:
    #     ADD_NLU_FLAG('CELEB__user_mentioned_celeb')
    ADD_NLU_FLAG('CELEB__discuss_movie')
    ADD_NLU_FLAG('CELEB__discuss_tv')
    ADD_NLU_FLAG('CELEB__discuss_song')
    ADD_NLU_FLAG('CELEB__known_work')
    return

@nlu_processing
def get_background_flags(context):
    return