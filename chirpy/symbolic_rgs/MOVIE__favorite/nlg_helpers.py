from chirpy.response_generators.movie import movie_helpers
from chirpy.core.response_generator import nlg_helper
from chirpy.response_generators.movie.expression_lists import YES, NO

import logging
import re
import string

logger = logging.getLogger('chirpylogger')


@nlg_helper
def enter_movie(entity):
    # print(entity.__dict__)
    logger.warning(f'entity is {entity}')
    # logger.warning('entity is %s' % entity.talkable_name)
    return string.capwords(entity)
    # return string.capwords(entity.talkable_name)
    # return entity.talkable_name


@nlg_helper
def get_important_scene(entity):
    import openai
    openai.api_key = "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"

    def generate(prompt, **kwargs):
        completion = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=256, temperature=0.7, **kwargs)
        return completion.choices[0].text
    
    return generate(
        f"Give one most memorable scene of the movie {entity} in a sentence as if you are talking to a friend, starting with 'My favorite scene of the movie was'."
    )[1:]