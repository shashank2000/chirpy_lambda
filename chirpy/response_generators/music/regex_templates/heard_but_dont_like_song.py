from chirpy.core.regex.util import *
from chirpy.core.regex.regex_template import RegexTemplate
from chirpy.response_generators.music.expression_lists import *
from chirpy.response_generators.food.regex_templates.word_lists import *

class HeardButDoNotLikeTemplate(RegexTemplate):
    slots = {
        'no_word': NO + RARE_WORDS,
        'like_word': LIKE_CLAUSES,
        'dislike_word': DISLIKE_CLAUSES,
        'yes_word': YES_WORDS
    }
    templates = [
        OPTIONAL_TEXT_PRE + "(don\'t|do not) {like_word}" + OPTIONAL_TEXT_POST,
        OPTIONAL_TEXT_PRE + "(?<!don't ){dislike_word}" + OPTIONAL_TEXT_POST,
        "{yes_word}" + OPTIONAL_TEXT_MID + "but" + OPTIONAL_TEXT_POST,
        "{like_word} but" + OPTIONAL_TEXT_POST,
        "i {like_word} but" + OPTIONAL_TEXT_POST,
    ]
    positive_examples = [
        ('i don\'t like them', {'like_word': 'like'}),
    ]
    negative_examples = [
        'yeah',
        ('no', {'no_word': 'no'}),
    ]