from chirpy.core.response_generator.regex_templates import *
from chirpy.response_generators.wiki2 import wiki_helpers
from chirpy.core.regex.templates import *
from chirpy.core.response_generator.nlu import nlu_processing
from enum import IntEnum, auto
from typing import Set, List
import logging

logger = logging.getLogger('chirpylogger')


class ResponseType(IntEnum):
    """
    Base Response Types
    """
    DISINTERESTED = auto()  # User displays negative navigational intent
    CHANGE_TOPIC = auto()  # User indicates intention to change topic
    REQUEST_REPEAT = auto()
    YES = auto()  # User responds with a statement that contains a yes-phrase
    NO = auto()  # User responds with a statement that contains a no-phrase
    QUESTION = auto()  # User asks a question
    COMPLAINT = auto()
    DONT_KNOW = auto()  # User says they don't know
    DIDNT_KNOW = auto()  # User says they didn't know, probably in response to a TIL
    THATS = auto()  # User says "That's interesting" or something similar
    NOTHING = auto()  # User says "nothing", "i
    BACKCHANNEL = auto() # that's cool, okay, yes, nice


def add_response_types(response_type_enum, additional_response_types: List[str]):
    """
    Returns an IntEnum named 'ResponseType' with additional response types
    :param response_type_enum:
    :param additional_response_types:
    :return:
    """
    response_types = [i.name for i in response_type_enum]
    response_types += additional_response_types
    return IntEnum('ResponseType',
                   [(response_type, auto()) for response_type in response_types]
                   )


def identify_base_response_types(rg, utterance) -> Set[ResponseType]:
    retval = set()
    if is_disinterested(rg, utterance):
        retval.add(ResponseType.DISINTERESTED)

    if is_change_topic(rg, utterance):
        retval.add(ResponseType.CHANGE_TOPIC)

    if is_request_repeat(rg, utterance):
        retval.add(ResponseType.REQUEST_REPEAT)

    if is_no(rg, utterance):
        retval.add(ResponseType.NO)

    if is_yes(rg, utterance):
        retval.add(ResponseType.YES)

    if is_question(rg, utterance):
        retval.add(ResponseType.QUESTION)

    if is_complaint(rg, utterance):
        retval.add(ResponseType.COMPLAINT)

    if is_dont_know_response(rg, utterance):
        retval.add(ResponseType.DONT_KNOW)

    if is_didnt_know_response(rg, utterance):
        retval.add(ResponseType.DIDNT_KNOW)

    if is_thats_response(rg, utterance):
        retval.add(ResponseType.THATS)

    if is_nothing_response(rg, utterance):
        retval.add(ResponseType.NOTHING)

    if is_backchannel(rg, utterance):
        retval.add(ResponseType.BACKCHANNEL)

    return retval

def global_response_type_dict(rg, utterance):
    vals = identify_base_response_types(rg, utterance)
    return {v : (v in vals) for v in ResponseType.__members__.values()}


@nlu_processing
def get_intent_flags(context, state_manager, utterance):
    if (
        state_manager.current_state.navigational_intent.neg_intent or
        DisinterestedTemplate().execute(utterance) is not None
    ):
        ADD_NLU_FLAG("GlobalFlag__DISINTERESTED")
    if (
        NoTemplate().execute(utterance) is not None or 
        state_manager.current_state.dialogact['is_no_answer']
    ):
        ADD_NLU_FLAG("GlobalFlag__NO")
    if (
        YesTemplate().execute(utterance) is not None or 
        state_manager.current_state.dialogact['is_yes_answer']
    ):
        ADD_NLU_FLAG("GlobalFlag__YES")
    if state_manager.current_state.question['is_question']:
        ADD_NLU_FLAG("GlobalFlag__QUESTION")
    if state_manager.current_state.dialogact['top_1'] == 'complaint':
        ADD_NLU_FLAG("GlobalFlag__COMPLAINT")
    if ChangeTopicTemplate().execute(utterance) is not None:
        ADD_NLU_FLAG("GlobalFlag__CHANGE_TOPIC")
    if RequestRepeatTemplate().execute(utterance) is not None or SayThatAgainTemplate().execute(utterance) is not None:
        ADD_NLU_FLAG("GlobalFlag__REQUEST_REPEAT")
    
    template_match = DontKnowTemplate().execute(utterance) is not None
    is_difficult = any(
        [x in utterance for x in ['tough', 'tricky', 'difficult']]
    ) #and rg.get_current_entity(initiated_this_turn=True) is None TODO fix
    if template_match or is_difficult:
        ADD_NLU_FLAG("GlobalFlag__DONT_KNOW")
    if ThatsTemplate().execute(utterance) is not None:
        ADD_NLU_FLAG("GlobalFlag__THATS")
    if (
        DidntKnowTemplate().execute(utterance) is not None or 
        (SurprisedReallyTemplate().execute(utterance) is not None and len(utterance) <= 15)
    ):
        ADD_NLU_FLAG("GlobalFlag__DIDNT_KNOW")
    if NotThingTemplate().execute(utterance) is not None:
        ADD_NLU_FLAG("GlobalFlag__NOTHING")
    if BackChannelingTemplate().execute(utterance) is not None:
        ADD_NLU_FLAG("GlobalFlag__BACKCHANNEL")

    wiki_helpers.add_flags(context, ADD_NLU_FLAG)