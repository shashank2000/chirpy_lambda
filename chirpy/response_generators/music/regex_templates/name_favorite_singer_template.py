from chirpy.core.regex.util import *
from chirpy.core.regex.regex_template import RegexTemplate
from chirpy.response_generators.music.expression_lists import *
from chirpy.response_generators.music.regex_templates.word_lists import *
from chirpy.response_generators.food.regex_templates.word_lists import *
from chirpy.databases.datalib.music_database import music_singer_gpt, music_singer_str_wiki

class NameFavoriteSingerTemplate(RegexTemplate):
    slots = {
        'keyword_singer': ['singer', 'artist', 'musician', 'band'],
        'favorite': NONEMPTY_TEXT,
        'positive_adjective': POSITIVE_ADJECTIVES,
        'positive_verb': POSITIVE_VERBS,
        'positive_adverb': POSITIVE_ADVERBS,
        'frequency_adverb': FREQUENCY_ANSWERS,
        'listen_word': ['listening to', 'hearing', 'listened to', 'heard', 'have been listening to', 'have been hearing', 'to listen to', 'listen to'],
        'yes_word': YES_WORDS,
        'ending': '([.!]|)$'
    }
    templates = [
        "i {positive_verb} {listen_word} {favorite}{ending}",
        "my favorite {keyword_singer} is {favorite}{ending}",
        "my favorite is {favorite}{ending}",
        "my favorite {keyword_singer} of all time is {favorite}{ending}",
        "my favorite of all time is {favorite}{ending}",
        "my favorite {keyword_singer} is probably {favorite}{ending}",
        "my favorite is probably {favorite}{ending}",
        "my favorite {keyword_singer} of all time is probably {favorite}{ending}",
        "my favorite of all time is probably {favorite}{ending}",
        "i {positive_verb} {favorite}{ending}",
        "i {positive_adverb} {positive_verb} {favorite}{ending}",
        "i think {favorite} is {positive_adjective}",
        OPTIONAL_TEXT_PRE + "my favorite {keyword_singer} is {favorite}{ending}",
        OPTIONAL_TEXT_PRE + "my favorite is {favorite}{ending}",
        OPTIONAL_TEXT_PRE + "i {positive_verb} {favorite}{ending}",
        OPTIONAL_TEXT_PRE + "i {positive_adverb} {positive_verb} {favorite}{ending}",
        OPTIONAL_TEXT_PRE + "i think {favorite} is {positive_adjective}" + OPTIONAL_TEXT_POST,
        "probably {favorite}{ending}",
        OPTIONAL_TEXT_PRE + "probably {favorite}{ending}",
        "i'd have to say {favorite}{ending}",
        "i guess i'd have to say {favorite}{ending}",
        "maybe {favorite}{ending}",
        "i guess {favorite}{ending}",
        "i think {favorite}{ending}",
        OPTIONAL_TEXT_PRE + "i'd have to say {favorite}{ending}",
        OPTIONAL_TEXT_PRE + "i guess i'd have to say {favorite}{ending}",
        OPTIONAL_TEXT_PRE + "maybe {favorite}{ending}",
        OPTIONAL_TEXT_PRE + "i guess {favorite}{ending}",
        OPTIONAL_TEXT_PRE + "i think {favorite}{ending}",
        "{yes_word} i {listen_word} {favorite}{ending}",
        "{yes_word} i recently {listen_word} {favorite}{ending}",
        "{yes_word} lately i {listen_word} {favorite}{ending}",
        "{yes_word} i {listen_word} {favorite} recently" + OPTIONAL_TEXT_POST,
        "{yes_word} i {listen_word} {favorite} lately" + OPTIONAL_TEXT_POST,
        "{yes_word} i just {listen_word} {favorite}{ending}",
        "i {listen_word} {favorite}{ending}",
        "i recently {listen_word} {favorite}{ending}",
        "lately i {listen_word} {favorite}{ending}",
        "i {listen_word} {favorite} recently" + OPTIONAL_TEXT_POST,
        "i {listen_word} {favorite} lately" + OPTIONAL_TEXT_POST,
        "i just {listen_word} {favorite}{ending}",
        "i've heard {favorite}{ending}",
        "i've just heard {favorite}{ending}",
        OPTIONAL_TEXT_PRE + "{yes_word} i {listen_word} {favorite}{ending}",
        OPTIONAL_TEXT_PRE + "{yes_word} i recently {listen_word} {favorite}{ending}",
        OPTIONAL_TEXT_PRE + "{yes_word} lately i {listen_word} {favorite}{ending}",
        OPTIONAL_TEXT_PRE + "{yes_word} i {listen_word} {favorite} recently" + OPTIONAL_TEXT_POST,
        OPTIONAL_TEXT_PRE + "{yes_word} i {listen_word} {favorite} lately" + OPTIONAL_TEXT_POST,
        OPTIONAL_TEXT_PRE + "{yes_word} i just {listen_word} {favorite}{ending}",
        OPTIONAL_TEXT_PRE + "i {listen_word} {favorite}{ending}",
        OPTIONAL_TEXT_PRE + "i recently {listen_word} {favorite}{ending}",
        OPTIONAL_TEXT_PRE + "lately i {listen_word} {favorite}{ending}",
        OPTIONAL_TEXT_PRE + "i {listen_word} {favorite} recently" + OPTIONAL_TEXT_POST,
        OPTIONAL_TEXT_PRE + "i {listen_word} {favorite} lately" + OPTIONAL_TEXT_POST,
        OPTIONAL_TEXT_PRE + "i just {listen_word} {favorite}{ending}",
        "{yes_word} {favorite}{ending}",
        OPTIONAL_TEXT_PRE + "{yes_word} {favorite}{ending}",
        "i {frequency_adverb} {positive_verb} {favorite}{ending}",
        "i {frequency_adverb} {listen_word} {favorite}{ending}",
        "i {frequency_adverb} {positive_verb} {listen_word} {favorite}{ending}"
    ]

    positive_examples = []
    negative_examples = []

class NameFavoriteSingerWithDatabaseTemplate(RegexTemplate):
    slots = {
        'database_singer': list(music_singer_gpt.keys()) + list(music_singer_str_wiki.keys())
    }

    templates = [
        OPTIONAL_TEXT_PRE + "[\'\"]?{database_singer}[.!\'\"]?" + OPTIONAL_TEXT_POST
    ]

    positive_examples = []
    negative_examples = []