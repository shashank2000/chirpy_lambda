from chirpy.core.regex.util import *
from chirpy.core.regex.regex_template import RegexTemplate
from chirpy.response_generators.music.expression_lists import *
from chirpy.response_generators.food.regex_templates.word_lists import *


class DoNotPlayInstrTemplate(RegexTemplate):
    slots = {}

    templates = [
        OPTIONAL_TEXT_PRE + "don't" + OPTIONAL_TEXT_MID + "play" + OPTIONAL_TEXT_POST,
        OPTIONAL_TEXT_PRE + 'not' + OPTIONAL_TEXT_MID + 'play' + OPTIONAL_TEXT_POST,
        OPTIONAL_TEXT_PRE + 'do not' + OPTIONAL_TEXT_MID + 'play' + OPTIONAL_TEXT_POST,
        OPTIONAL_TEXT_PRE + "can't" + OPTIONAL_TEXT_POST + "play" + OPTIONAL_TEXT_POST,
        OPTIONAL_TEXT_PRE + "cannot" + OPTIONAL_TEXT_POST + "play" + OPTIONAL_TEXT_POST
    ]

    positive_examples = [
        ("i don't")
    ]
    negative_examples = []
