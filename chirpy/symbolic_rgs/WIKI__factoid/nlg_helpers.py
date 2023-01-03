from chirpy.core.entity_linker.entity_linker import WikiEntity
from chirpy.core.response_generator import nlg_helper, ResponseType
from chirpy.core.state_manager import StateManager

from chirpy.response_generators.wiki2 import wiki_utils, wiki_response_generator, wiki_infiller, blacklists
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

logger = logging.getLogger('chirpylogger')

es = wiki_utils.es

@nlg_helper
def get_overview(rg, entity):
    query = {
        "query": {
            "match": {
                "doc_title": entity
            }
        }
    }
    result = es.search(index='enwiki-20201201-sections', body=query, size=1)
    if not result or result['hits']['total']['value'] == 0:
        logger.warning(f"Could not find overview for {entity}. Indicative of mismatch between entity linker and wiki corpus")
        return None
    section = wiki_utils.convert_to_dict(result['hits']['hits'][0])
    summary = wiki_utils.get_summary(section['text'], wiki_utils.get_sentseg_fn(rg), max_words=50, max_sents=2)
    logger.primary_info(f"Summary is: {summary}")
    summary = wiki_utils.clean_wiki_text(summary)
    logger.primary_info(f"Summary after clean is: {summary}")
    if wiki_utils.contains_offensive(summary):
        logger.primary_info(f"Found {entity}'s overview: {summary} to be offensive, discarding it")
        return None
    return summary



def get_wiki_sentences(cur_entity: WikiEntity, state_manager: StateManager, first_turn: bool):
    sections = wiki_utils.get_text_for_entity(cur_entity.name)
    sentences = wiki_utils.get_sentences_from_sections_tfidf(sections, state_manager, first_turn=first_turn)
    return sentences

def execute_infiller(input_data, infiller_cache):
    if infiller_cache is not None:
        # assert not include_acknowledgements, "Infiller cache should only be set while prompting"
        logger.primary_info(f"Using the infiller cache.")
        return infiller_cache
    if os.environ['usecolbert']:
        infiller_results = wiki_infiller.call_colbertinfiller(
            input_data.get('tuples'),
            input_data.get('sentences'),
            input_data.get('max_length'),
            input_data.get('contexts', tuple()),
            input_data.get('prompts', tuple()),
        )
    else:
        infiller_results = wiki_infiller.call_infiller(
            input_data.get('tuples'),
            input_data.get('sentences'),
            input_data.get('max_length'),
            input_data.get('contexts', tuple()),
            input_data.get('prompts', tuple()),
        )
    return infiller_results

def select_best_response(state_manager: StateManager, utterance, responses, contexts, prompts, acknowledgements=None) -> Tuple[str, str]:
    """

    :param utterance:
    :param responses:
    :param contexts:
    :param prompts:
    :param acknowledgements: an optional list of acknowledgements to rank
    :return: Returns top_res, top_ack (optional)
    """
    ranker = ResponseRanker(state_manager)
    top_ack = None
    if acknowledgements:
        scores = wiki_infiller.get_scores(ranker, utterance, acknowledgements + responses)
        if scores['error']:
            logger.primary_info("Scores failed")
            return None, None
        ack_scores, response_scores = wiki_utils.split_dict_with_length(scores, len(acknowledgements))
        logger.primary_info(f"After splitting: {ack_scores} {response_scores}")

        ack_gpt_scores = ack_scores['score']
        ack_dialogpt_scores = ack_scores['updown']
        ack_scores = [(a - b*2) for a, b in zip(ack_gpt_scores, ack_dialogpt_scores)]
        logger.primary_info(f"ack_scores: {ack_scores}")
        top_ack = acknowledgements[ack_scores.index(min(ack_scores))].strip()
        # TODO: better handling of terminal punctuation
        if not top_ack.endswith('.') and not top_ack.endswith('?'): top_ack += '.'
    else:
        response_scores = wiki_infiller.get_scores(ranker, utterance, responses)
        if response_scores is None or response_scores['error']:
            logger.primary_info("Scores failed")
            return None, None

    res_gpt_scores = [-math.log(x) for x in response_scores['score']]
    res_dialogpt_scores = response_scores['updown']
    res_scores = [(dialogpt_score - gpt_score*0.25) for gpt_score, dialogpt_score in zip(res_gpt_scores, res_dialogpt_scores)]
    logger.primary_info(f"res_scores: {res_scores}")
    logger.primary_info('\n'.join([f"{sc:.3f} ({gpt_sc:.3f} {dgpt_sc:.3f}) {utt} [{context}]"
                                    for sc, gpt_sc, dgpt_sc, utt, context in zip(res_scores, res_gpt_scores, res_dialogpt_scores, responses, contexts)]))

    best_completion_idx = res_scores.index(max(res_scores))
    top_res = responses[best_completion_idx].strip()
    # TODO: better handling of terminal punctuation
    if not top_res.endswith('.') and not top_res.endswith('?'): top_res += '.'

    logger.primary_info(f"Wiki infiller context used: {contexts[best_completion_idx]}")
    logger.primary_info(f"Wiki infiller template used: {prompts[best_completion_idx]}")

    return top_res, top_ack

USE_INFILLER = False

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

    if USE_INFILLER:
        if len(sentences) < 4:
            logger.primary_info("Infiller does not have enough sentences to work with")
            return None, None

        ## Step 2a: Get the relevant templates for the entity
        # Retrieve questions, text.
        specific_responses, best_ent_group = wiki_infiller.get_templates(cur_entity)
        if specific_responses is None:
            return None, None
        # specific_responses example:
        # [["In my opinion, the best place for [clothing] is [store].", ["clothing", "fashion", "retailer", "dress", "suits"]]]
        ## Step 2b:
        # We replace pronouns on second one onwards.
        # Note that this is irrelevant for the prompt case, since we reconstruct the prompts later anyway.
        pronouns = wiki_response_generator.get_pronoun(best_ent_group, sentences)
        prompt_to_pronoun_prompt = {prompt: wiki_infiller.replace_entity_placeholder(prompt, pronouns, cur_entity.talkable_name, omit_first=True)
                                    for (prompt, _) in specific_responses}
        specific_responses = [(prompt_to_pronoun_prompt[a], b) for (a, b) in specific_responses]
        # logger.primary_info(f"After replacement: {specific_questions} {type(specific_questions[0])}")

        specific_responses = [q for q in specific_responses if q[0] not in state_manager.current_state.WIKI__EntityState[cur_entity.name].templates_used]

        input_data = {
            'tuples': tuple((q[0], tuple(q[1])) for q in specific_responses),
            'sentences': tuple(s.strip().strip('.') for s in sentences), # TODO tuple(s.strip().strip('.') for s in sentences),
            'max_length': 40
        }

        execute_neural = None
        acknowledgements = None

        ### BEGIN THREADING ###
        thread = threading.currentThread()
        should_kill = getattr(thread, "killable", False)
        if should_kill:
            logger.primary_info(f"Infiller interior call detected to be running in a killable thread.")
        is_done = getattr(thread, "isKilled", False)

        def initializer(killable: bool):
            threading.currentThread().killable = killable
            threading.currentThread().isKilled = is_done

        infiller_cache = state_manager.current_state.cache['infiller']

        with futures.ThreadPoolExecutor(max_workers=2, initializer=initializer, initargs=(should_kill,)) as executor:
            if execute_neural:
                neural_future = executor.submit(execute_neural)
            infiller_future = executor.submit(execute_infiller, input_data, infiller_cache)
        ### END THREADING ###

        if execute_neural:
            acknowledgements = neural_future.result()

        infiller_results = infiller_future.result()

        if infiller_results['error']:
            logger.primary_info("Infiller failed")
            return None, None

        if acknowledgements is not None:
            acknowledgements = wiki_infiller.filter_responses(state_manager, acknowledgements, cur_entity.name)
            logger.primary_info(f"Got acknowledgements: {acknowledgements}")

        state_manager.current_state.cache['infiller'] = infiller_results

        responses = infiller_results['completions']
        prompts = infiller_results['prompts']

        # TODO check this -- why is this only done for smooth transition? ANS: It will replace the first occurrence of entity with the pronoun.
        # if smooth_transition:
        #     logger.primary_info(f"Responses before pronouns treatment: {responses}")
        #     pronouns = get_pronoun(best_ent_group, sentences)
        #     pronoun_prompt_to_prompt = {b: a for (a, b) in prompt_to_pronoun_prompt.items()}
        #     responses = [revert_to_entity_placeholder(response, cur_entity.name, pronoun_prompt_to_prompt[prompt]) for response, prompt in zip(responses, prompts)]
        #     responses = [replace_entity_placeholder(response, pronouns) for response in responses]
        #     logger.primary_info(f"Responses after pronouns treatment: {responses}")

        responses = wiki_infiller.filter_responses(state_manager, responses, cur_entity.name)

        logger.primary_info(f"Got responses: {responses}")

        prompts = infiller_results['prompts']
        contexts = infiller_results['contexts']

        utterance = state_manager.current_state.text
        return select_best_response(state_manager, utterance, responses, contexts, prompts, acknowledgements)
    else:
        return random.choice(sentences), None

@nlg_helper
def get_factoid(entity: Optional[WikiEntity], state_manager: StateManager):
    top_res, top_ack = get_infilling_statement(entity, state_manager, first_turn=True)
    return top_res