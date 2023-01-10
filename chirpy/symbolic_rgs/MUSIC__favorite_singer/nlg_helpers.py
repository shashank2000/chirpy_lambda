import random
import re

from chirpy.core.response_generator import nlg_helper
import chirpy.response_generators.music.response_templates.general_templates as templates
from chirpy.response_generators.wiki2.wiki_utils import get_til_title

@nlg_helper
def least_repetitive_compliment(context):
	return context.state_manager.current_state.choose_least_repetitive(templates.compliment_user_musician_choice())

@nlg_helper
def pick_til(tils):
	til = re.sub(r'\(.*?\)', '', random.choice(tils)[0])
	return templates.til(til)

@nlg_helper
def get_tils(singer_name):
	return get_til_title(singer_name)