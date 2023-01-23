from chirpy.core.response_generator.nlu import nlu_processing

@nlu_processing
def get_flags(context):
    pos_val = context.flags['GlobalFlag__YES']
    ADD_NLU_FLAG('MOVIE__user_likes_movie', pos_val)


@nlu_processing
def get_background_flags(context):
    ADD_NLU_FLAG('MOVIE__user_likes_movie', pos_val)