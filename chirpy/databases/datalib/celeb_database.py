import json
import os

from chirpy.databases.databases import database_lookup, database_exists

CELEB_OPINION_FILE = os.path.join(os.path.dirname(__file__), 'individual_celeb_opinions.json')
CELEB_WORK_OPINION_FILE = os.path.join(os.path.dirname(__file__), 'celeb_work_opinions.json')

import logging

logger = logging.getLogger('chirpylogger')


# load food database
with open(CELEB_OPINION_FILE) as f:
    celeb_opinion = json.load(f)

@database_exists("celeb_opinion")
def verify_celeb_exists(celeb_name : str):
    return celeb_name in celeb_opinion

@database_lookup("celeb_opinion")
def lookup_celeb(celeb_name : str):
    return celeb_opinion[celeb_name]

# load celeb database
with open(CELEB_WORK_OPINION_FILE) as f:
    celeb_work_opinion = json.load(f)

@database_exists("celeb_work_opinion")
def verify_celeb_work_exists(work_name : str):
    return work_name in celeb_work_opinion.keys()

@database_lookup("celeb_work_opinion")
def lookup_celeb_work(work_name : str):
    return celeb_work_opinion[work_name]
