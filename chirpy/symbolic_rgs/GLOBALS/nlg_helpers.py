from chirpy.core.entity_linker.entity_linker import WikiEntity
from chirpy.core.response_generator import nlg_helper
from chirpy.core.state_manager import StateManager

from chirpy.response_generators.wiki2 import wiki_utils

from typing import Optional, Tuple
import logging
import random

logger = logging.getLogger('chirpylogger')

es = wiki_utils.es



def get_wiki_sentences(cur_entity: WikiEntity, state_manager: StateManager, first_turn: bool):
    sections = wiki_utils.get_text_for_entity(cur_entity.name)
    sentences = wiki_utils.get_sentences_from_sections_tfidf(sections, state_manager, first_turn=first_turn)
    return sentences

def get_infilling_statement(entity: WikiEntity, state_manager: StateManager, first_turn: bool) -> Tuple[Optional[str], Optional[str]]:
    """
    Get an infilled statement, optionally with acknowledgement infilled as well.

    :param entity:
    :return: (top response, top acknowledgement)
    """

    # state, utterance, response_types = rg.get_state_utterance_response_types()
    cur_entity = entity

    ## STEP 1: Get Wiki sections and the sentences from those sections
    sentences = get_wiki_sentences(cur_entity, state_manager, first_turn)
    logger.primary_info(f"Wiki sentences are: {sentences}")

    # TODO: Use infiller
    return random.choice(sentences).strip(), None

@nlg_helper
def get_factoid(entity: Optional[WikiEntity], state_manager: StateManager):
    if entity is None:
        return None
    top_res, top_ack = get_infilling_statement(entity, state_manager, first_turn=True)
    return top_res