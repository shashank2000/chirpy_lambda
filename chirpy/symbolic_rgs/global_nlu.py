from chirpy.core.response_generator.nlu import *
import logging
import re
import string

logger = logging.getLogger('chirpylogger')

from chirpy.core.regex.regex_template import RegexTemplate
from chirpy.core.regex.util import OPTIONAL_TEXT_POST, OPTIONAL_TEXT_PRE, OPTIONAL_TEXT_MID

class AreYouRecordingTemplate(RegexTemplate):
	slots = {
		'RECORD': ['record', 'recorded', 'records', 'recording'],
		'modifier': ['have', 'will be', 'will', 'are', 'like', 'like to', 'want to']
	}

	templates = [
		OPTIONAL_TEXT_PRE + "you {RECORD}" + OPTIONAL_TEXT_POST,
		OPTIONAL_TEXT_PRE + "you {modifier} {RECORD}" + OPTIONAL_TEXT_POST
	]

	positive_examples = [
		("do you record conversations", {'RECORD': 'record'}),
		("are you recording this", {'RECORD': 'recording'}),
		("are you recording this without my consent", {'RECORD': 'recording'}),
		("alexa are you recording this conversation", {'RECORD': 'recording'}),
		("echo are you recording this conversation", {'RECORD': 'recording'}),
		("alexa have you recorded our conversations", {'RECORD': 'recorded'}),
		("i bet you have recorded our conversations", {"RECORD": "recorded", "modifier": "have"}),
		("do you like recording conversations", {"modifier": "like", "RECORD": "recording"})

	]

	negative_examples = [
		"the government might be recording this interaction",
		"i don't like people listening in on my conversations",
		"you know people like to record conversations"
	]

BASE_PATH = os.path.dirname(__file__)

def load_redquestion_list(category):
	with open(os.path.join(BASE_PATH, '..', 'core', 'red_question', category + '.txt'), 'r') as f:
		return [x.strip() for x in f]

IDENTITY_QUESTIONS = [
	((r'[\w\s\']*your name[\w\s]*', r'[\w\s\']*you called[\w\s]*'),  "Sorry, I can't tell you my real name. I have to remain anonymous for the Alexa Prize competition. But you can still call me Alexa if you want."),
	((r'[\w\s\']*who are you$', r'[\w\s\']*who are you alexa$', r'[\w\s\']*who you are$', r'[\w\s\']*who you are alexa$', r'[\w\s\']*who built you$', r'[\w\s\']*who made you$', r'[\w\s\']*who are you made by$',
	  r'[\w\s\']*what are you$', r'[\w\s\']*tell me about yourself[\w\s]*', r'[\w\s\']*tell me about you$', r'[\w\s\']*tell me about you alexa$'), 'I am an Alexa Prize social bot built by a university.'),
	((r'[\w\s\']*where[\w\s\']*you[\w\s]*live', r'[\w\s\']*where[\w\s\']*you[\w\s\']*from', r'[\w\s\']*where are you( |$)[\w\s\']*'), 'I live in the cloud. It\'s quite comfortable since it\'s so soft.')
]

WHATS_YOUR_NAME = [r'[\w\s\']*your name[\w\s]*', r'[\w\s\']*you called[\w\s]*']
WHO_MADE_YOU = [r'[\w\s\']*who are you$', r'[\w\s\']*who are you alexa$', r'[\w\s\']*who you are$', r'[\w\s\']*who you are alexa$', r'[\w\s\']*who built you$', r'[\w\s\']*who made you$', r'[\w\s\']*who are you made by$', r'[\w\s\']*what are you$', r'[\w\s\']*tell me about yourself[\w\s]*', r'[\w\s\']*tell me about you$', r'[\w\s\']*tell me about you alexa$']
WHERE_ARE_YOU = [r'[\w\s\']*where[\w\s\']*you[\w\s]*live', r'[\w\s\']*where[\w\s\']*you[\w\s\']*from', r'[\w\s\']*where are you( |$)[\w\s\']*']

RED_QUESTION_TYPES = ['financial']
RQ_TYPE_TO_TOKENS = {kind : load_redquestion_list(kind) for kind in RED_QUESTION_TYPES}

def preprocess(token : str):
	token = token.lower()
	token = ''.join([x for x in token if x in string.ascii_lowercase])
	return token
	
def classify_utterance(utterance : str, rq_type : str):
	# tokens = [preprocess(word) for word in utterance.split(' ')]
	# tokens = [x for x in tokens if len(x)]
	n_bad = 0
	logger.warning(f"Red question: utterance is {utterance}, tokens are {RQ_TYPE_TO_TOKENS[rq_type][:10]}")
	for token in RQ_TYPE_TO_TOKENS[rq_type]:
		if token in utterance:
			n_bad += 1
	if n_bad > 0:
		return True
	## todo add more nuanced handling
	return False
	
def utterance_contains_word(utterance, word):
	"""
	Returns True iff utterance contains word surrounded by either spaces or apostrophes.
	
	i.e. if word="siri", then
	utterance="do you like siri" -> True
	utterance="do you like siri's voice" -> True
	utterance="I like the greek god osiris" -> False
	"""
	tokens = re.split(" |'", utterance)  # split by space or apostrophe
	return word in tokens

@nlu_processing
def get_flags(context):
	utterance = context.utterance
	if 'what' in utterance:
		ADD_NLU_FLAG("GlobalFlag__WHAT")
	if 'why' in utterance:
		ADD_NLU_FLAG("GlobalFlag__WHY")
		
	# Other virtual assistants
	if any(re.match(q, utterance) for q in WHATS_YOUR_NAME):
		ADD_NLU_FLAG("GlobalFlag__WhatsYourName")
	if any(re.match(q, utterance) for q in WHO_MADE_YOU):
		ADD_NLU_FLAG("GlobalFlag__WhoMadeYou")
	if any(re.match(q, utterance) for q in WHERE_ARE_YOU):
		ADD_NLU_FLAG("GlobalFlag__WhereAreYou")
		
	for virtual_assistant in ['siri', 'cortana']:
		if utterance_contains_word(utterance, virtual_assistant):
			ADD_NLU_FLAG("GlobalFlag__VirtualAssistantCompetitor")
	
	# Red question
	# <=3 word utterances are not asking for advice (bold assumption!)
	if len(utterance.split(' ')) > 3:
		# Run classifier for legal/financial/medical questions
		for rq_type in RED_QUESTION_TYPES:
			if classify_utterance(utterance, rq_type):
				ADD_NLU_FLAG(f"GlobalFlag__RedQuestion__{rq_type.capitalize()}")
		
		if AreYouRecordingTemplate().execute(utterance) is not None:
			ADD_NLU_FLAG("GlobalFlag__AreYouRecording")
	
	return None
	
	