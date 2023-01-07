from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List, Any, Optional, Tuple
from concurrent import futures
import random 


import inflect
engine = inflect.engine()

from chirpy.core.entity_linker.entity_linker_classes import WikiEntity
from chirpy.core.camel.variable import Variable
from chirpy.core.camel.pipes import get_pipe
from chirpy.core.util import infl 
from chirpy.annotators.blenderbot import BlenderBot
from chirpy.core.response_generator.neural_helpers import get_neural_fallback_handoff, neural_response_filtering
from chirpy.core.response_generator.neural_helpers import is_two_part, NEURAL_DECODE_CONFIG, get_random_fallback_neural_response

import os

BASE_PATH = os.path.join(os.path.dirname(__file__), '../../symbolic_rgs')


import logging
logger = logging.getLogger('chirpylogger')

class NLGNode(ABC):
    @abstractmethod
    def generate(self, context):
        pass

def get_neural_response_given_history(context, history, prefix=None):
    """
    Sends history to BlenderBot and returns response.
    
    Args:
        history: history of utterances in the conversation thus far
        prefix: utterance prefix that the generated utterance should begin with
    
    Returns:
         response: str, or None in case of error or nothing suitable. Guaranteed to end in a sentence-ending token.
    """
    if prefix:
        # If there's a prefix, we aren't retrieving the prefetched and cached response.
        # We have to run a generation call again.
        bbot = BlenderBot(context.state_manager)
        return bbot.execute(input_data={'history': history}, prefix=prefix)
    if isinstance(context.state_manager.current_state.blenderbot, futures.Future):
        # Sometimes the call to BlenderBot has not yet finished, in which case we store the future
        # in self.state_manager.current_state.blenderbot and retrieve the result here.
        future_result = context.state_manager.current_state.blenderbot.result()
        # Replace the future with the future's result
        setattr(context.state_manager.current_state, 'blenderbot', future_result)
    return context.state_manager.current_state.blenderbot # (responses, scores)


def transform_questions_into_statements(responses, scores):
    """
    Filters through a series of related responses + scores.
    - If the response contains 0 questions, keep it as is.
    - If the response starts with a question, delete it.
    - Otherwise, keep only the part before the first question.
    """
    out = []
    for response, score in zip(responses, scores):
        if '?' in response:
            sentences = [x.strip() for x in response.split('.')]
            first_question_index = min([i for i in range(len(sentences)) if '?' in sentences[i]])
            if first_question_index == 0: continue
            response = '. '.join(sentences[:first_question_index])
        out.append((response, score))
    if len(out) == 0: return [], []
    return zip(*out)
    
def get_best_neural_response(responses, scores, history, conditions):
    """
    
    @param responses: list of strings. responses from neural module. Can assume all end in sentence-ending tokens.
    @param history: list of strings. the neural conversation so far (up to and including the most recent user utterance).
    @return: best_response: string, or None if there was nothing suitable.
    
    """
    num_questions = len([response for response in responses if '?' in response])
    is_majority_questions = num_questions >= len(responses) / 2
    responses, _ = neural_response_filtering(responses, scores)
    responses = [r for r in responses if 'thanks' not in responses]
    
    for cond in conditions:
        responses = [r for r in responses if cond(r)]
    
    if len(responses) == 0:
        logger.warning('There are 0 suitable neural responses')
        return None
    responses = sorted(responses,
                       key=lambda response: (  # all these keys should be things where higher is good
                           ('?' in response) if is_majority_questions or len(history)==1 else ('?' not in response),
                            is_two_part(response),
                            len(response),
                       ),
                       reverse=True)
    return responses[0]

def get_neural_response(context, prefix=None, allow_questions=False, conditions=None) -> Optional[str]:
    """
    Get neurally generated response started with specific prefix
    :param prefix: Prefix
    :param allow_questions: whether to allow questions in the response
    :param conditions: list of funcs that filter for desired response
    :return:
    """
    if conditions is None: conditions = []
    history = context.state_manager.current_state.history + [context.utterance]
    responses, scores = get_neural_response_given_history(context, history, prefix=prefix)
    if not allow_questions:
        responses, scores = transform_questions_into_statements(responses, scores)
        responses_scores = [(response, score) for response, score in zip(responses, scores) if '?' not in response]
        if len(responses_scores) == 0:
            logger.info("There are 0 suitable neural responses.")
            return None
        responses, scores = zip(*responses_scores)
    best_response = get_best_neural_response(responses, scores, history, conditions=conditions)
    return best_response

@dataclass
class NeuralGeneration(NLGNode):
    prefix : NLGNode
    def generate(self, context):
        return get_neural_response(context, prefix=self.prefix.generate(context))

@dataclass
class Val(NLGNode):
    variable : Variable
    operations : List[Tuple[str, str]]
    def generate(self, context):
        value = self.variable.generate(context)
        for operator, operation in self.operations:
            if operator == '|':
                value = get_pipe(operation)(value)
            elif operator == '+':
                value += int(operation)
            elif operator == '-':
                value -= int(operation)
        return value
        
@dataclass
class NLGHelper:
    name : str
    args : List[NLGNode]
    def generate(self, context):
        assert hasattr(context.supernode.nlg_helpers, self.name), f"Function not found: {self.name} (available: {dir(context.supernode.nlg_helpers).filter(lambda x: not x.startswith('_'))})"
        args = [arg.generate(context) for arg in self.args]
        return getattr(context.supernode.nlg_helpers, self.name)(*args)

@dataclass
class Inflect:
    inflect_token : NLGNode
    inflect_entity : Variable
    def generate(self, context):
        input = self.inflect_token.generate(context)
        val = self.inflect_entity.generate(context)
        assert isinstance(val, WikiEntity), f"@inflect: Val {val} is not a WikiEntity"
        return infl(input, val.is_plural)

@dataclass
class InflectEngine(NLGNode):
    type : NLGNode
    string : NLGNode
    def generate(self, context):
        input = self.string.generate(context)
        return getattr(engine, self.type.generate(context))(input)

@dataclass
class OneOf(NLGNode):
    options : List[NLGNode]
    def generate(self, context):
        return random.choice(self.options).generate(context)
        
@dataclass
class Constant(NLGNode):
    val : Any
    def generate(self, context):
        return eval(self.val) # haha
        
@dataclass
class String(NLGNode):
    string : str
    def generate(self, context):
        return self.string
    def __repr__(self):
        return '"' + self.string + '"'
        
SENTENCE_END_PUNCTUATION = ['.', '?', '!']
PUNCTUATION = ['.', ',', '?', '!', ':', ';']
        

def spacingaware_join(x):
    result = ""
    for idx, item in enumerate(x):
        assert isinstance(item, str), f"Item {item} (from {x}) is not a string"
        if idx != 0 and not any(item.startswith(punct) for punct in PUNCTUATION):
            result += " "
        if idx != 0 and len(item) and any(x[idx - 1].endswith(punct) for punct in SENTENCE_END_PUNCTUATION):
            item = item[0].upper() + item[1:]
        result += item
    return result

@dataclass
class NLGList(NLGNode):
    items : List[NLGNode]
    def generate(self, context):
        return spacingaware_join([x.generate(context) for x in self.items])