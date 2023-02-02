import json
import os

from chirpy.databases.databases import database_lookup, database_exists

MOVIE_INFO_FILE = os.path.join(os.path.dirname(__file__), 'movie_info.json')
ACTOR_INFO_FILE = os.path.join(os.path.dirname(__file__), 'actor_info.json')

import logging

logger = logging.getLogger('chirpylogger')


# load movie database
with open(MOVIE_INFO_FILE) as f:
    movie_info = json.load(f)

with open(ACTOR_INFO_FILE) as f:
    actor_info = json.load(f)


@database_exists("movie_info")
def verify_movie_exists(movie_name: str):
    return movie_name in movie_info.keys()


@database_lookup("movie_info")
def lookup_movie(movie_name: str):
    if verify_movie_exists(movie_name):
        return movie_info[movie_name]
    return {
        "main_actor": None, 
        "director": None, 
        "genre": None, 
        "plot": None, 
        "most_memorable_scene": None
    }


@database_exists("actor_info")
def verify_actor_exists(actor_name: str):
    return actor_name in actor_info.keys()


@database_lookup("actor_info")
def lookup_actor(actor_name: str):
    if verify_actor_exists(actor_name):
        return actor_info[actor_name]
    return {
        "movie_name": None
    }
