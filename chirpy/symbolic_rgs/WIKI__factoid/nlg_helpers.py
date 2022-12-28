from chirpy.core.entity_linker.entity_linker import WikiEntity
from chirpy.core.response_generator import nlg_helper, ResponseType
from chirpy.core.response_generator.symbolic_response_generator import SymbolicResponseGenerator

from chirpy.response_generators.wiki2 import wiki_utils, wiki_response_generator, wiki_infiller, blacklists
from chirpy.response_generators.wiki2.response_templates import response_components

from chirpy.annotators.blenderbot import BlenderBot
from chirpy.annotators.responseranker import ResponseRanker

from concurrent import futures
from typing import Optional, Tuple
import logging
import threading
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



def get_recommended_entity(rg: SymbolicResponseGenerator, state=None, initiated_this_turn=True):
    if state is not None:
        pass
    else:
        state = rg.state
    entity = rg.get_current_entity(initiated_this_turn)

    if initiated_this_turn and not entity and rg.get_last_active_rg() == 'TRANSITION':
        entity = rg.get_current_entity()

    # import pdb; pdb.set_trace()
    if entity:
        if entity.is_category:
            logger.primary_info(f"Recommended entity {entity} is a category, not using it for WIKI")
        elif entity.name in blacklists.ENTITY_BLACK_LIST or wiki_utils.remove_parens(entity.name) in blacklists.ENTITY_BLACK_LIST:
            logger.primary_info(f"Recommended entity {entity} is blacklisted for WIKI")
        elif entity.name in state.entity_state and state.entity_state[entity.name].finished_talking:
            logger.primary_info(f"Wiki has finished talking about recommended entity {entity}")
        else:
            logger.primary_info(f"Recommending entity {entity}: {entity.name}.")
            return entity
    logger.primary_info("Wiki didn't find an entity; returning.")
    return None

def get_wiki_sentences(rg: SymbolicResponseGenerator, cur_entity):
    sections = wiki_utils.get_text_for_entity(cur_entity.name)
    sentences = wiki_utils.get_sentences_from_sections_tfidf(sections, rg.state_manager,
                                                                first_turn=rg.active_last_turn())
    return sentences

def get_infilling_ack_components(rg: SymbolicResponseGenerator, top_da):
    """

    :param top_da: top dialog act
    :return:
    """
    state, utterance, response_types = rg.get_state_utterance_response_types()
    infilling_ack_context = None
    infilling_ack_prompts = None

    if top_da in ['statement', 'opinion', 'comment']:
        # agree with user
        infilling_ack_context = utterance
        infilling_ack_prompts = response_components.STATEMENT_ACKNOWLEDGEMENT_TEMPLATES
    elif ResponseType.POS_SENTIMENT in response_types or ResponseType.APPRECIATIVE in response_types:
        infilling_ack_context = rg.get_conversation_history()[-1]
        infilling_ack_prompts = response_components.APPRECIATION_ACKNOWLEDGEMENT_TEMPLATES
    return infilling_ack_context, infilling_ack_prompts

def execute_infiller(rg: SymbolicResponseGenerator, input_data):
    infiller_cache = rg.get_cache('infiller')
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

def select_best_response(self, utterance, responses, contexts, prompts, acknowledgements=None) -> Tuple[str, str]:
    """

    :param utterance:
    :param responses:
    :param contexts:
    :param prompts:
    :param acknowledgements: an optional list of acknowledgements to rank
    :return: Returns top_res, top_ack (optional)
    """
    ranker = ResponseRanker(self.state_manager)
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

def get_infilling_statement(rg: SymbolicResponseGenerator, entity: Optional[WikiEntity] = None, neural_ack=False, infill_ack=False) -> Tuple[Optional[str], Optional[str]]:
    """
    Get an infilled statement, optionally with acknowledgement infilled as well.

    :param entity:
    :return: (top response, top acknowledgement)
    """

    print(1)

    state, utterance, response_types = rg.get_state_utterance_response_types()
    cur_entity = entity

    ## STEP 1: Get Wiki sections and the sentences from those sections
    sentences = get_wiki_sentences(rg, cur_entity)
    print(1.5, sentences)
    logger.primary_info(f"Wiki sentences are: {sentences}")
    if len(sentences) < 4:
        logger.primary_info("Infiller does not have enough sentences to work with")
        return None, None

    print(2)

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
    specific_responses = [q for q in specific_responses if q[0] not in state.entity_state[cur_entity.name].templates_used]

    print(3)

    input_data = {
        'tuples': tuple((q[0], tuple(q[1])) for q in specific_responses),
        'sentences': tuple(s.strip().strip('.') for s in sentences), # TODO tuple(s.strip().strip('.') for s in sentences),
        'max_length': 40
    }

    execute_neural = None
    acknowledgements = None

    print(4)

    if infill_ack:
        top_da = rg.get_top_dialogact()
        infilling_ack_context, infilling_ack_prompts = get_infilling_ack_components(top_da)
        input_data.update({
            'contexts': tuple([infilling_ack_context] * len(infilling_ack_prompts)),
            'prompts': tuple(infilling_ack_prompts),
        })
    elif neural_ack:
        MAX_HISTORY_UTTERANCES = 3
        history = rg.state_manager.current_state.history[-(MAX_HISTORY_UTTERANCES - 1):]   # TODO: if we're changing topic, don't use history
        def execute_neural():
            responses, _ = BlenderBot(rg.state_manager).execute(input_data={'history': history+[utterance]})
            return responses

    ### BEGIN THREADING ###
    thread = threading.currentThread()
    should_kill = getattr(thread, "killable", False)
    if should_kill:
        logger.primary_info(f"Infiller interior call detected to be running in a killable thread.")
    is_done = getattr(thread, "isKilled", False)

    def initializer(killable: bool):
        threading.currentThread().killable = killable
        threading.currentThread().isKilled = is_done

    with futures.ThreadPoolExecutor(max_workers=2, initializer=initializer, initargs=(should_kill,)) as executor:
        if execute_neural:
            neural_future = executor.submit(execute_neural)
        infiller_future = executor.submit(execute_infiller, rg, input_data)
    ### END THREADING ###

    if execute_neural:
        acknowledgements = neural_future.result()

    infiller_results = infiller_future.result()

    if infiller_results['error']:
        logger.primary_info("Infiller failed")
        return None, None

    if infill_ack:
        # if need_to_infill_acknowledgements:
        # Cut up the responses, if we asked for acknowledgement generation
            # import pdb; pdb.set_trace()
        ack_results, infiller_results = wiki_utils.split_dict_with_length(infiller_results, len(infilling_ack_prompts))
        acknowledgements = ack_results['completions']

    if acknowledgements is not None:
        acknowledgements = wiki_infiller.filter_responses(rg, acknowledgements, cur_entity.name)
        logger.primary_info(f"Got acknowledgements: {acknowledgements}")

    rg.set_cache('infiller', infiller_results)

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

    responses = wiki_infiller.filter_responses(rg, responses, cur_entity.name)

    logger.primary_info(f"Got responses: {responses}")

    prompts = infiller_results['prompts']
    contexts = infiller_results['contexts']

    return select_best_response(utterance, responses, contexts, prompts, acknowledgements)

@nlg_helper
def get_factoid(rg: SymbolicResponseGenerator, entity: Optional[WikiEntity] = None):
    print("entity12421", entity)
    print("entity2", get_recommended_entity(rg))
    print(1)
    top_res, top_ack = get_infilling_statement(rg, entity)
    return top_res