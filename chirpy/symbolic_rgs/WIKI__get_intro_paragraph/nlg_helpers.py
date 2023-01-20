from chirpy.core.entity_linker.entity_linker import WikiEntity
from chirpy.core.response_generator import nlg_helper, ResponseType
from chirpy.core.state_manager import StateManager

from chirpy.response_generators.wiki2 import wiki_utils
from chirpy.response_generators.wiki2.response_templates import response_components

from chirpy.annotators.blenderbot import BlenderBot
from chirpy.annotators.responseranker import ResponseRanker

from concurrent import futures
from typing import Optional, Tuple
import logging
import threading
import random
import math
import os

logger = logging.getLogger("chirpylogger")

es = wiki_utils.es


@nlg_helper
def get_intro_paragraph(entity):
    overview = wiki_utils.overview_entity(entity, wiki_utils.get_sentseg_fn, max_sents=4)
    if not overview:
        logger.info("No overview found")
        return None
    return overview
