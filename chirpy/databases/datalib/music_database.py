import json
import os

from chirpy.databases.databases import database_lookup, database_exists

MUSIC_INSTRUMENT_GPT_DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'json/music_instrument_gpt.json')
MUSIC_COMPOSITION_GPT_DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'json/music_composition_gpt.json')
MUSIC_COMPOSITION_STR_WIKI_DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'json/music_composition_str_wiki.json')
MUSIC_SINGER_GPT_DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'json/music_singer_gpt.json')
MUSIC_SINGER_STR_WIKI_DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'json/music_singer_str_wiki.json')
MUSIC_SONG_GPT_DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'json/music_song_gpt.json')
MUSIC_SONG_STR_WIKI_DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'json/music_song_str_wiki.json')
MUSIC_GENRE_GPT_DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'json/music_genre_gpt.json')
MUSIC_GENRE_STR_WIKI_DATABASE_FILE = os.path.join(os.path.dirname(__file__), 'json/music_genre_str_wiki.json')

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
with open(MUSIC_COMPOSITION_GPT_DATABASE_FILE) as f:
    music_composition_gpt = json.load(f)

@database_exists("music_composition")
def verify_music_composition_gpt_exists(composition_name: str):
    return composition_name in music_composition_gpt.keys()

@database_lookup("music_composition")
def lookup_music_composition_gpt_gpt(composition_name: str):
    return music_composition_gpt[composition_name]

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
def lookup_music_genre_gpt(genre_name: str):
    return music_genre_gpt[genre_name]

# load music_composition_str_wiki database
with open(MUSIC_COMPOSITION_STR_WIKI_DATABASE_FILE) as f:
    music_composition_str_wiki = json.load(f)

@database_exists("music_composition_str_wiki")
def verify_music_composition_str_wiki_exists(composition_name: str):
    return composition_name in music_composition_str_wiki.keys()

@database_lookup("music_composition_str_wiki")
def lookup_music_composition_str_wiki(composition_name: str):
    return music_composition_str_wiki[composition_name]

# load music_singer_str_wiki database
with open(MUSIC_SINGER_STR_WIKI_DATABASE_FILE) as f:
    music_singer_str_wiki = json.load(f)

@database_exists("music_singer_str_wiki")
def verify_music_song_str_wiki_exists(singer_name: str):
    return singer_name in music_singer_str_wiki.keys()

@database_lookup("music_singer_str_wiki")
def lookup_music_singer_str_wiki(singer_name: str):
    return music_singer_str_wiki[singer_name]

# load music_song_str_wiki database
with open(MUSIC_SONG_STR_WIKI_DATABASE_FILE) as f:
    music_song_str_wiki = json.load(f)

@database_exists("music_song_str_wiki")
def verify_music_song_str_wiki_exists(song_name: str):
    return song_name in music_song_str_wiki.keys()

@database_lookup("music_song_str_wiki")
def lookup_music_song_str_wiki(song_name: str):
    return music_song_str_wiki[song_name]

# load music_genre_str_wiki database
with open(MUSIC_GENRE_STR_WIKI_DATABASE_FILE) as f:
    music_genre_str_wiki = json.load(f)

@database_exists("music_genre_str_wiki")
def verify_music_genre_str_wiki_exists(genre_name: str):
    return genre_name in music_genre_str_wiki.keys()

@database_lookup("music_genre_str_wiki")
def lookup_music_genre_str_wiki(genre_name: str):
    return music_genre_str_wiki[genre_name]



