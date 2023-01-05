#from chirpy.response_generators.food.food_helpers import get_intro_acknowledgement, sample_food_containing_ingredient, get_attribute
# from chirpy.response_generators.food import food_helpers
from chirpy.core.response_generator import nlg_helper, nlg_helper_augmented
import logging
import random
import openai

logger = logging.getLogger('chirpylogger')

openai.api_key = "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"

def generate(prompt, **kwargs):
    completion = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=256, temperature=0.7,
                                          **kwargs)
    return completion.choices[0]


@nlg_helper
def get_movie_from_actor(actor: str):
    output = generate(
        f"""
            Return a movie name by the actor: {actor} in the format: movie_name.
            """
    )['text']

    return output.strip()


@nlg_helper
def get_movie_desc(movie: str):
    output = generate(
        f"""
            Give a one line description of the move: {movie}. Start your response with 'It is a movie in which'
            """
    )['text']

    return output.strip()

