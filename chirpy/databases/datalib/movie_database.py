import json
import os

from chirpy.databases.databases import database_lookup, database_exists

MOVIE_INFO_FILE = os.path.join(os.path.dirname(__file__), 'movie_info.json')

import logging

logger = logging.getLogger('chirpylogger')


# load movie database
with open(MOVIE_INFO_FILE) as f:
    movie_info = json.load(f)

@database_exists("movie_info")
def verify_movie_exists(movie_name : str):
    return movie_name in movie_info.keys()

@database_lookup("movie_info")
def lookup_movie_actor(movie_name : str):
    return movie_info[movie_name]["main_actor"]

@database_lookup("movie_info")
def lookup_movie_director(movie_name : str):
    return movie_info[movie_name]["director"]

@database_lookup("movie_info")
def lookup_movie_genre(movie_name : str):
    return movie_info[movie_name]["genre"]

@database_lookup("movie_info")
def lookup_movie_plot(movie_name : str):
    return movie_info[movie_name]["plot"]

@database_lookup("movie_info")
def lookup_movie_scene(movie_name : str):
    return movie_info[movie_name]["most_memorable_scene"]