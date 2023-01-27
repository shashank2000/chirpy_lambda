from chirpy.core.regex.regex_template import RegexTemplate
from chirpy.response_generators.music.expression_lists import *
from chirpy.databases.datalib.music_database import music_instrument_gpt

class NameFavoriteInstrumentWithDatabaseTemplate(RegexTemplate):
    slots = {
        'database_instr': list(music_instrument_gpt.keys())
    }

    templates = [
        OPTIONAL_TEXT_PRE + "{database_instr}" + OPTIONAL_TEXT_POST
    ]

    positive_examples = []
    negative_examples = []


