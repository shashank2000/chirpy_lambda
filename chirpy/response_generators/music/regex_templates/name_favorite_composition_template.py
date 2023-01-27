from chirpy.core.regex.util import *
from chirpy.core.regex.regex_template import RegexTemplate
from chirpy.response_generators.music.expression_lists import *
from chirpy.response_generators.food.regex_templates.word_lists import *
from chirpy.databases.datalib.music_database import music_composition_comment_gpt


class NameFavoriteCompositionTemplate(RegexTemplate):
    slots = {
        'keyword_song': ['composition', 'song'],
        'favorite': NONEMPTY_TEXT,
        'positive_adjective': POSITIVE_ADJECTIVES,
        'positive_verb': POSITIVE_VERBS,
        'positive_adverb': POSITIVE_ADVERBS,
        'play_word': ['playing', 'play' 'played', 'have been playing'],
        'yes_word': YES_WORDS,
    }
    templates = [
        "i {positive_verb} {play_word} {favorite}",
        "i {positive_adverb} {positive_verb} to {play_word} {favorite}",
        "my favorite {keyword_song} is {favorite}",
        "my favorite is {favorite}",
        "my favorite {keyword_song} of all time is {favorite}",
        "my favorite of all time is {favorite}",
        "my favorite {keyword_song} is probably {favorite}",
        "my favorite is probably {favorite}",
        "my favorite {keyword_song} of all time is probably {favorite}",
        "my favorite of all time is probably {favorite}",
        "i {positive_verb} {favorite}",
        "i {positive_adverb} {positive_verb} {favorite}",
        "i think {favorite} is {positive_adjective}",
        OPTIONAL_TEXT_PRE + "my favorite {keyword_song} is {favorite}",
        OPTIONAL_TEXT_PRE + "my favorite is {favorite}",
        OPTIONAL_TEXT_PRE + "i {positive_verb} {favorite}",
        OPTIONAL_TEXT_PRE + "i {positive_adverb} {positive_verb} {favorite}",
        OPTIONAL_TEXT_PRE + "i think {favorite} is {positive_adjective}",
        "probably {favorite}",
        OPTIONAL_TEXT_PRE + "probably {favorite}",
        "i'd have to say {favorite}",
        "i guess i'd have to say {favorite}",
        "maybe {favorite}",
        "i guess {favorite}",
        "i think {favorite}",
        OPTIONAL_TEXT_PRE + "i'd have to say {favorite}",
        OPTIONAL_TEXT_PRE + "i guess i'd have to say {favorite}",
        OPTIONAL_TEXT_PRE + "maybe {favorite}",
        OPTIONAL_TEXT_PRE + "i guess {favorite}",
        OPTIONAL_TEXT_PRE + "i think {favorite}",
        "{yes_word} i {play_word} {favorite}",
        "{yes_word} i recently {play_word} {favorite}",
        "{yes_word} lately i {play_word} {favorite}",
        "{yes_word} i {play_word} {favorite} recently",
        "{yes_word} i {play_word} {favorite} lately",
        "{yes_word} i just {play_word} {favorite}",
        "i {play_word} {favorite}",
        "i recently {play_word} {favorite}",
        "lately i {play_word} {favorite}",
        "i {play_word} {favorite} recently",
        "i {play_word} {favorite} lately",
        "i just {play_word} {favorite}",
        "i've heard {favorite}",
        "i've just heard {favorite}",
        OPTIONAL_TEXT_PRE + "{yes_word} i {play_word} {favorite}",
        OPTIONAL_TEXT_PRE + "{yes_word} i recently {play_word} {favorite}",
        OPTIONAL_TEXT_PRE + "{yes_word} lately i {play_word} {favorite}",
        OPTIONAL_TEXT_PRE + "{yes_word} i {play_word} {favorite} recently",
        OPTIONAL_TEXT_PRE + "{yes_word} i {play_word} {favorite} lately",
        OPTIONAL_TEXT_PRE + "{yes_word} i just {play_word} {favorite}",
        OPTIONAL_TEXT_PRE + "i {play_word} {favorite}",
        OPTIONAL_TEXT_PRE + "i recently {play_word} {favorite}",
        OPTIONAL_TEXT_PRE + "lately i {play_word} {favorite}",
        OPTIONAL_TEXT_PRE + "i {play_word} {favorite} recently",
        OPTIONAL_TEXT_PRE + "i {play_word} {favorite} lately",
        OPTIONAL_TEXT_PRE + "i just {play_word} {favorite}",
        "{yes_word} {favorite}",
        OPTIONAL_TEXT_PRE + "{yes_word} {favorite}"
    ]

    positive_examples = [
        ('i really like to play zigeunerweisen', {'positive_adverb': 'really', 'positive_verb': 'like',
                                                  'play_word': 'play', 'favorite': 'zigeunerweisen'}),
        ('i really like to play la campanella', {'positive_adverb': 'really', 'positive_verb': 'like',
                                                  'play_word': 'play', 'favorite': 'la campanella'})

    ]
    negative_examples = [
        ('i really like to play la campanella', {'positive_adverb': 'really', 'positive_verb': 'like',
                                                 'favorite': 'to play la campanella'})
    ]

class NameFavoriteCompositionWithDatabaseTemplate(RegexTemplate):
    slots = {
        'database_composition': list(music_composition_comment_gpt.keys())
    }

    templates = [
        OPTIONAL_TEXT_PRE + "{database_composition}" + OPTIONAL_TEXT_POST
    ]

    positive_examples = []
    negative_examples = []
