from chirpy.response_generators.movie import movie_helpers
from chirpy.core.response_generator import nlg_helper
from chirpy.response_generators.movie.expression_lists import YES, NO

import logging
import ast

logger = logging.getLogger('chirpylogger')


@nlg_helper
def get_user_reasons(sentence):
    logger.warning(f'Utilities: {sentence}')
    import openai
    openai.api_key = "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"

    def generate(prompt, **kwargs):
        completion = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=256, temperature=0.7, **kwargs)
        return completion.choices[0]
    
    output = generate(
        f"""
        List the reasons why the user liked the movie and return it as an object. For instance,
        if the commentary is 'I liked the movie since I like the director and the actors',
        then the correct analysis would include 'director' and 'actors'.

        User commentary: {sentence}
        """
    )['text']

    all_keys = ast.literal_eval(output)
    return list(all_keys.keys())