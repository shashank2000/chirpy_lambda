from chirpy.response_generators.personal_issues import personal_issues_helpers 
from chirpy.response_generators.personal_issues import response_templates 
from chirpy.core.response_generator import nlg_helper, add_template
import logging
import random

logger = logging.getLogger('chirpylogger')

add_template(response_templates.PartialSubsequentTurnResponseTemplate)

@nlg_helper 
def response_contains_question(rg, response):
    return '?' in response