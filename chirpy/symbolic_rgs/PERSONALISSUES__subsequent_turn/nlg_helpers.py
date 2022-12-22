from chirpy.response_generators.personal_issues import personal_issues_helpers 
from chirpy.response_generators.personal_issues import response_templates 
from chirpy.core.response_generator import nlg_helper
import logging
import random

logger = logging.getLogger('chirpylogger')

@nlg_helper 
def response_contains_question(rg, response):
    return '?' in response