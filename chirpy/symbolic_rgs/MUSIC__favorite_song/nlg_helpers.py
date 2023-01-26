import random
import re

from chirpy.core.response_generator import nlg_helper

import chirpy.response_generators.music.response_templates.general_templates as templates
from chirpy.response_generators.wiki2.wiki_utils import get_til_title

@nlg_helper
def get_plural_form(work_descriptor):
    return work_descriptor + 's'
