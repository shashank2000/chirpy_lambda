from chirpy.core.regex.util import *
from chirpy.core.regex.regex_template import RegexTemplate
from chirpy.response_generators.music.expression_lists import *
from chirpy.response_generators.music.regex_templates.word_lists import *
from chirpy.response_generators.food.regex_templates.word_lists import *
from chirpy.databases.datalib.music_database import music_composition_gpt, music_composition_str_wiki


class NameFavoriteCompositionTemplate(RegexTemplate):
    slots = {
        'keyword_song': ['composition', 'song'],
        'favorite': NONEMPTY_TEXT,
        'positive_adjective': POSITIVE_ADJECTIVES,
        'positive_verb': POSITIVE_VERBS,
        'positive_adverb': POSITIVE_ADVERBS,
        'frequency_adverb': FREQUENCY_ANSWERS,
        'play_word': ['have been playing', 'playing', 'play' 'played', 'to play'],
        'yes_word': YES_WORDS,
        'ending': '([.!]||with .+)$'
    }
    templates = [
        "i {positive_adverb} {positive_verb} {play_word} {favorite}{ending}",
        "i {positive_verb} {play_word} {favorite}{ending}",
        "my favorite {keyword_song} is {favorite}{ending}",
        "my favorite is {favorite}{ending}",
        "my favorite {keyword_song} of all time is {favorite}{ending}",
        "my favorite of all time is {favorite}{ending}",
        "my favorite {keyword_song} is probably {favorite}{ending}",
        "my favorite is probably {favorite}{ending}",
        "my favorite {keyword_song} of all time is probably {favorite}{ending}",
        "my favorite of all time is probably {favorite}{ending}",
        "i {positive_verb} {favorite}{ending}",
        "i {positive_adverb} {positive_verb} {favorite}{ending}",
        "i think {favorite} is {positive_adjective}{ending}",
        OPTIONAL_TEXT_PRE + "my favorite {keyword_song} is {favorite}{ending}",
        OPTIONAL_TEXT_PRE + "my favorite is {favorite}{ending}",
        OPTIONAL_TEXT_PRE + "i {positive_verb} {favorite}{ending}",
        OPTIONAL_TEXT_PRE + "i {positive_adverb} {positive_verb} {favorite}{ending}",
        OPTIONAL_TEXT_PRE + "i think {favorite} is {positive_adjective}{ending}",
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
        "{yes_word} i {play_word} {favorite}{ending}",
        "{yes_word} i recently {play_word} {favorite}{ending}",
        "{yes_word} lately i {play_word} {favorite}{ending}",
        "{yes_word} i {play_word} {favorite} recently" + OPTIONAL_TEXT_POST,
        "{yes_word} i {play_word} {favorite} lately" + OPTIONAL_TEXT_POST,
        "{yes_word} i just {play_word} {favorite}{ending}",
        "i {play_word} {favorite}{ending}",
        "i recently {play_word} {favorite}{ending}",
        "lately i {play_word} {favorite}{ending}",
        "i {play_word} {favorite} recently" + OPTIONAL_TEXT_POST,
        "i {play_word} {favorite} lately" + OPTIONAL_TEXT_POST,
        "i just {play_word} {favorite}{ending}",
        "i've heard {favorite}{ending}",
        "i've just heard {favorite}{ending}",
        OPTIONAL_TEXT_PRE + "{yes_word} i {play_word} {favorite}{ending}",
        OPTIONAL_TEXT_PRE + "{yes_word} i recently {play_word} {favorite}{ending}",
        OPTIONAL_TEXT_PRE + "{yes_word} lately i {play_word} {favorite}{ending}",
        OPTIONAL_TEXT_PRE + "{yes_word} i {play_word} {favorite} recently" + OPTIONAL_TEXT_POST,
        OPTIONAL_TEXT_PRE + "{yes_word} i {play_word} {favorite} lately" + OPTIONAL_TEXT_POST,
        OPTIONAL_TEXT_PRE + "{yes_word} i just {play_word} {favorite}{ending}",
        OPTIONAL_TEXT_PRE + "i {play_word} {favorite}{ending}",
        OPTIONAL_TEXT_PRE + "i recently {play_word} {favorite}{ending}",
        OPTIONAL_TEXT_PRE + "lately i {play_word} {favorite}{ending}",
        OPTIONAL_TEXT_PRE + "i {play_word} {favorite} recently" + OPTIONAL_TEXT_POST,
        OPTIONAL_TEXT_PRE + "i {play_word} {favorite} lately" + OPTIONAL_TEXT_POST,
        OPTIONAL_TEXT_PRE + "i just {play_word} {favorite}{ending}",
        "{yes_word} {favorite}{ending}",
        OPTIONAL_TEXT_PRE + "{yes_word} {favorite}{ending}",
        "i {frequency_adverb} go for {favorite}{ending}",
        "i {frequency_adverb} {positive_verb} {favorite}{ending}",
        "i {frequency_adverb} {play_word} {favorite}{ending}",
        "i {frequency_adverb} {positive_verb} {listen_word} {favorite}{ending}"
    ]

    positive_examples = [
    ]

    negative_examples = [
    ]

class NameFavoriteCompositionWithDatabaseTemplate(RegexTemplate):
    slots = {
        'database_composition': list(music_composition_gpt.keys()) + list(music_composition_str_wiki.keys())
    }

    templates = [
        OPTIONAL_TEXT_PRE + "{database_composition}[.!]?" + OPTIONAL_TEXT_POST
    ]

    positive_examples = []
    negative_examples = []
