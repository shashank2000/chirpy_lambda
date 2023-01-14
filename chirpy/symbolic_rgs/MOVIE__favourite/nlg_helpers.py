#from chirpy.response_generators.food.food_helpers import get_intro_acknowledgement, sample_food_containing_ingredient, get_attribute
# from chirpy.response_generators.food import food_helpers
from chirpy.core.response_generator import nlg_helper, nlg_helper_augmented
import logging
import random
import openai

logger = logging.getLogger('chirpylogger')

# openai.api_key =
#
# def generate(prompt, **kwargs):
#     completion = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=256, temperature=0.7,
#                                           **kwargs)
#     return completion.choices[0]

#
# @nlg_helper
# def get_movie_actor(movie: str):
#     output = generate(
#         f"""
#             Give the main actor's name in the movie: {movie} in the format: actor_name.
#             """
#     )['text']
#
#     return output.strip()
#
#
# @nlg_helper
# def get_movie_director(movie: str):
#     output = generate(
#         f"""
#             Give the director's name in the movie: {movie} in the format: director_name.
#             """
#     )['text']
#
#     return output.strip()
#
#
# @nlg_helper
# def get_movie_genre(movie: str):
#     output = generate(
#         f"""
#             What is the genre of the movie: {movie} in the format: genre_name.
#             """
#     )['text']
#
#     return output.strip()

# INTRO_STATEMENTS = [
#     "Ah yes, [FOOD] [copula] one of my favorite things to eat up here in the cloud.",
#     "Oh yeah, [FOOD] [copula] such an amazing choice. It's one of my favorite foods up here in the cloud."
# ]
#
# @nlg_helper
# def sample_food_containing_ingredient(food: str):
#     food = food.lower()
#     logger.warning(f"Food is: {food}")
#     logger.warning(f"{[item for item, item_data in food_helpers.FOODS.items() if ('ingredients' in item_data and food in item_data['ingredients'])]}")
#     return random.choice([item for item, item_data in food_helpers.FOODS.items() if ('ingredients' in item_data and food in item_data['ingredients'])])
#
# @nlg_helper
# def get_food_origin(food):
#     if not food_helpers.is_known_food(food):
#         return None
#     food_data = food_helpers.get_food_data(food)
#     logger.warning(f"FACTOID includes ORIGIN: {'origin' in food_data}")
#     if 'origin' in food_data:
#         return food_data['origin']
#     return None
#
# YEAR_ENDINGS = ['st', 'th', 'nd', 'rd', ' century', 'BC']
#
# @nlg_helper
# def get_food_year(food):
#     if not food_helpers.is_known_food(food):
#         return None
#     food_data = food_helpers.get_food_data(food)
#
#     if 'year' not in food_data:
#         return None
#
#     year = food_data['year'].strip()
#
#     # the 4th century BC
#     if 'century' in year or ' BC' in year:
#         if 'the' not in year: year = "the " + year
#         return year
#
#     year = year.strip()
#     if year.endswith('s'):
#         intyear = int(year[:-1])
#     else:
#         intyear = int(year)
#     if intyear > 1800:
#         return None
#
#     return year
#
# @nlg_helper
# def get_food_ingredient(food: str):
#     return food_helpers.sample_ingredient(food)
#
# @nlg_helper
# def get_food_texture(food: str):
#     return food_helpers.get_texture(food)
#
# @nlg_helper
# def get_food_ingredient_of(food: str):
#     return food_helpers.sample_food_containing_ingredient(food)
#
#
# CUSTOM_STATEMENTS = {
#     'chocolate': "I especially love how rich and smooth it is."
# }
#
# @nlg_helper
# def get_custom_comment(cur_food):
#     return CUSTOM_STATEMENTS.get(cur_food, None)
#
