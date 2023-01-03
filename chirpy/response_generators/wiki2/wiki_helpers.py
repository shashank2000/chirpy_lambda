from chirpy.core.response_generator.response_type import add_response_types, ResponseType
from chirpy.core.camel.context import Context, get_global_flags
import logging
from chirpy.response_generators.wiki2.regex_templates import *
from chirpy.annotators.corenlp import Sentiment
from chirpy.response_generators.wiki2.response_templates.response_components import ERROR_ADMISSION, \
    APPRECIATION_DEFAULT_ACKNOWLEDGEMENTS, COMMISERATION_ACKNOWLEDGEMENTS

logger = logging.getLogger('chirpylogger')

ADDITIONAL_RESPONSE_TYPES = ['CONFUSED', 'WHAT_ABOUT_YOU', 'HIGH_INITIATIVE', 'POS_SENTIMENT', 'NEG_SENTIMENT',
                             'NEUTRAL_SENTIMENT', 'KNOW_MORE', 'PERSONAL_DISCLOSURE', 'AGREEMENT', 'DISAGREEMENT',
                             'APPRECIATIVE', 'OPINION', 'STARTS_WITH_WHAT']

ResponseType = add_response_types(ResponseType, ADDITIONAL_RESPONSE_TYPES)

def user_is_confused(context: Context, utterance: str):
    return (ClarificationQuestionTemplate().execute(utterance) and not context.state_manager.current_state.navigational_intent.pos_intent) \
           or DoubtfulTemplate().execute(utterance)

def is_high_initiative(context: Context, utterance: str):
    corenlp_output = context.state_manager.current_state.corenlp
    return not ((len(utterance) <= 4 and not corenlp_output['nouns'] and
                 not corenlp_output['proper_nouns']) or len(utterance) <= 3)

def get_sentiment(context: Context):
    return context.state_manager.current_state.corenlp['sentiment']

def is_pos_sentiment(context, utterance):
    return get_sentiment(context) in [Sentiment.POSITIVE, Sentiment.STRONG_POSITIVE]

def is_neg_sentiment(context: Context, utterance: str):
    return get_sentiment(context) in [Sentiment.NEGATIVE, Sentiment.STRONG_NEGATIVE]

def is_neutral_sentiment(context: Context, utterance: str):
    return get_sentiment(context) == Sentiment.NEUTRAL

def is_appreciative(context: Context, utterance: str):
    return context.state_manager.current_state.dialogact['top_1'] == 'appreciation' or AppreciativeTemplate().execute(utterance) is not None

def starts_with_what(context: Context, utterance: str):
    tokens = list(utterance.split())
    return 'what' in tokens[:3]

def user_wants_to_know_more(context: Context, utterance: str):
    return KnowMoreTemplate().execute(utterance) is not None

FIRST_PERSON_WORDS = {
    "i", "i'd", "i've", "i'll", "i'm",
    "me", "my", "myself", "mine"
}

def contains_first_person_word(utterance: str):
    tokens = set(utterance.split())
    return not tokens.isdisjoint(FIRST_PERSON_WORDS)

def is_personal_disclosure(context: Context, utterance: str):
    return contains_first_person_word(utterance) and len(utterance.split()) >= 5

def is_opinion(context: Context, utterance: str):
    return utterance.startswith('because') or \
           'opinion' in (context.state_manager.current_state.dialogact['top_1'], context.state_manager.current_state.dialogact['top_2']) or \
           any([utterance.startswith(x) for x in ['i believe', 'i think', 'i feel']])

# Wiki RG only
def is_no_to_sections(rg, utterance):
    state = rg.state
    tokens = set(utterance.split())
    if state and state.prev_treelet_str == rg.discuss_article_treelet.name:
        NO_WORDS = {'neither', 'else', 'nothing', 'none', "not"}
        return not tokens.isdisjoint(NO_WORDS)

def user_agrees(context: Context, utterance: str):
    return AgreementTemplate().execute(utterance) is not None

def user_disagees(context: Context, utterance: str):
    return DisagreementTemplate().execute(utterance) is not None

def original_til_templates(apologize: bool, original_til: str):
    APOLOGIZE_THEN_ORIGINAL = \
        ["Sometimes I get things wrong. ",
         "Every so often I have trouble understanding what I read. ",
         "Let's see if I can read it again more clearly this time. ",
         "Oh, sorry, maybe I misremembered the details. " ,
         "Ah, sorry, maybe I said it wrong. "]
    THEN_ORIGINAL = [
        f"I'll quote the source. I've read on wikipedia that {original_til}.",
        f"Going back to the original version, it said {original_til}.",
        f"What I saw on Wikipedia was that {original_til}.",
        f"Let's see, I think the original version was that {original_til}.",
        F"I remember the original version on Wikipedia saying that {original_til}."
    ]

    if apologize:
        return [a+b for (a, b) in zip(APOLOGIZE_THEN_ORIGINAL, THEN_ORIGINAL)]
    else:
        return THEN_ORIGINAL

def add_flags(context: Context, add_nlu_flag) -> set[str]:
    utterance = context.utterance
    if user_is_confused(context, utterance): add_nlu_flag('WIKI__CONFUSED')
    if is_neg_sentiment(context, utterance): add_nlu_flag('WIKI__NEG_SENTIMENT')
    if is_pos_sentiment(context, utterance): add_nlu_flag('WIKI__POS_SENTIMENT')
    if is_neutral_sentiment(context, utterance): add_nlu_flag('WIKI__NEUTRAL_SENTIMENT')
    if is_opinion(context, utterance): add_nlu_flag('WIKI__OPINION')
    if is_appreciative(context, utterance): add_nlu_flag('WIKI__APPRECIATIVE')

    if not context.flags['GlobalFlag__COMPLAINT'] and not context.flags['GlobalFlag__DISINTERESTED']:
        # to counter false positives, e.g. "that is not interesting"
        if user_wants_to_know_more(context, utterance):
            add_nlu_flag('WIKI__KNOW_MORE')

    if is_personal_disclosure(context, utterance): add_nlu_flag('WIKI__PERSONAL_DISCLOSURE')
    if user_disagees(context, utterance):
        add_nlu_flag('WIKI__DISAGREEMENT')
    else: # check is necessary to prevent false positives
        if user_agrees(context, utterance): add_nlu_flag('WIKI__AGREEMENT')
    # if is_no_to_sections(self, utterance): response_types.add(ResponseType.NO)
    if starts_with_what(context, utterance): add_nlu_flag('WIKI__STARTS_WITH_WHAT')
