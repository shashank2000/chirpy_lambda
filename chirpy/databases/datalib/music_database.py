import json
import os

from chirpy.databases.databases import database_lookup, database_exists

MUSIC_INSTRUMENT_GPT_DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'json/music_instrument_gpt.json')
MUSIC_COMPOSITION_COMMENT_GPT_DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'json/music_composition_comment_gpt.json')
MUSIC_COMPOSITION_COMPOSER_GPT_DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'json/music_composition_composer_gpt.json')
MUSIC_SINGER_GPT_DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'json/music_singer_gpt.json')
MUSIC_SONG_GPT_DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'json/music_song_gpt.json')
MUSIC_GENRE_GPT_DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'json/music_genre_gpt.json')

import logging

logger = logging.getLogger('chirpylogger')

# load music_instrument_gpt database
with open(MUSIC_INSTRUMENT_GPT_DATABASE_FILE) as f:
    music_instrument_gpt = json.load(f)

@database_exists("music_instrument")
def verify_music_instrument_gpt_exists(instrument_name: str):
    return instrument_name in music_instrument_gpt.keys()

@database_lookup("music_instrument")
def lookup_music_instrument_gpt_gpt(instrument_name: str):
    return music_instrument_gpt[instrument_name]

# load music_composition_comment_gpt database
with open(MUSIC_COMPOSITION_COMMENT_GPT_DATABASE_FILE) as f:
    music_composition_comment_gpt = json.load(f)

@database_exists("music_composition_comment")
def verify_music_composition_comment_gpt_exists(composition_name: str):
    return composition_name in music_composition_comment_gpt.keys()

@database_lookup("music_composition_comment")
def lookup_music_composition_comment_gpt_gpt(composition_name: str):
    return music_composition_comment_gpt[composition_name]

# load music_composition_composer_gpt database
with open(MUSIC_COMPOSITION_COMPOSER_GPT_DATABASE_FILE) as f:
    music_composition_composer_gpt = json.load(f)

@database_exists("music_composition_composer")
def verify_music_composition_composer_gpt_exists(composition_name: str):
    return composition_name in music_composition_composer_gpt.keys()

@database_lookup("music_composition_composer")
def lookup_music_composition_composer_gpt_gpt(composition_name: str):
    return music_composition_composer_gpt[composition_name]

# load music_singer_gpt database
with open(MUSIC_SINGER_GPT_DATABASE_FILE) as f:
    music_singer_gpt = json.load(f)

@database_exists("music_singer")
def verify_music_singer_gpt_exists(singer_name: str):
    return singer_name in music_singer_gpt.keys()

@database_lookup("music_singer")
def lookup_music_singer_gpt_gpt(singer_name: str):
    return music_singer_gpt[singer_name]

# load music_song_gpt database
with open(MUSIC_SONG_GPT_DATABASE_FILE) as f:
    music_song_gpt = json.load(f)

@database_exists("music_song")
def verify_music_song_gpt_exists(song_name: str):
    return song_name in music_song_gpt.keys()

@database_lookup("music_song")
def lookup_music_song_gpt_gpt(song_name: str):
    return music_song_gpt[song_name]

# load music_genre_gpt database
with open(MUSIC_GENRE_GPT_DATABASE_FILE) as f:
    music_genre_gpt = json.load(f)

@database_exists("music_genre")
def verify_music_genre_gpt_exists(genre_name: str):
    return genre_name in music_genre_gpt.keys()

@database_lookup("music_genre")
def lookup_music_genre_gpt_gpt(genre_name: str):
    return music_genre_gpt[genre_name]

