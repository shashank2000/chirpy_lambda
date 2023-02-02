from chirpy.core.regex.regex_template import RegexTemplate
from chirpy.response_generators.music.expression_lists import *
from chirpy.databases.datalib.music_database import music_genre_gpt, music_genre_str_wiki

class NameFavoriteGenreWithDatabaseTemplate(RegexTemplate):
    slots = {
        'database_genre': list(music_genre_gpt.keys())
    }

    templates = [
        OPTIONAL_TEXT_PRE + "[\'\"]?{database_genre}[.!\'\"]?" + OPTIONAL_TEXT_POST
    ]

    positive_examples = []
    negative_examples = []

class NameFavoriteGenreAbbrevWithDatabaseTemplate(RegexTemplate):
    slots = {
        'database_genre': list(music_genre_str_wiki.keys())
    }

    templates = [
        OPTIONAL_TEXT_PRE + "{database_genre}[.!]?" + OPTIONAL_TEXT_POST
    ]

    positive_examples = []
    negative_examples = []

