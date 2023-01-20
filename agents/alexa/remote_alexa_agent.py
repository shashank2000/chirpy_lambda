import boto3
import datetime
import jsonpickle
import logging

from agents.alexa.event import Event
from agents.remote_psql_persistent import RemotePersistentAgent
from chirpy.core.logging_utils import setup_logger, update_logger, PROD_LOGGER_SETTINGS
from chirpy.core import flags
from chirpy.core.util import get_function_version_to_display
from chirpy.core.canary import should_be_canary

# Timeout at the highest level, as close as possible to 10 seconds. Do nothing after, just create an apologetic
# response and send it over
OVERALL_TIMEOUT = 9.75 if flags.use_timeouts else flags.inf_timeout  # seconds

# Timeout for final_response function. Set at 9.35 seconds to comfortably log the latencies
FINAL_RESPONSE_TIMEOUT = 9.35 if flags.use_timeouts else flags.inf_timeout  #seconds

# Timeout for progressive response
PROGRESSIVE_RESPONSE_TIMEOUT = 3 if flags.use_timeouts else flags.inf_timeout  #seconds

# Timeout for NLP Pipeline
NLP_PIPELINE_TIMEOUT = 3 if flags.use_timeouts else flags.inf_timeout  #seconds

LATENCY_EXPERIMENT = False
LATENCY_BINS = [0, 1, 1.5, 2, 2.5]

DEFAULT_REPROMPT = "Sorry, I couldn't quite hear what you said. Could you repeat it please?".strip()

canary_lambda_client = boto3.client('lambda')
apology_string = 'Sorry, I\'m having a really hard time right now. ' + \
'I have to go, but I hope you enjoyed our conversation so far. ' + \
'Have a good day!'

logger = logging.getLogger('chirpylogger')
root_logger = logging.getLogger()
if not hasattr(root_logger, 'chirpy_handlers'):
    setup_logger(PROD_LOGGER_SETTINGS)

class RemoteAlexaAgent(RemotePersistentAgent):
    """
    Remote Alexa Agent.
    """
    def __init__(self, event):
        session_id, user_id, new_session, last_state_creation_time = self.get_constructor_args(event)
        super().__init__(session_id=session_id,
                       user_id=user_id,
                       new_session=new_session,
                       last_state_creation_time=last_state_creation_time)

    def get_constructor_args(self, event: Event):
        session_id = event.get('session.sessionId')
        user_id = event.get('session.user.userId')
        new_session = event.get('session.new')
        last_state_creation_time = event.get('request.timestamp')

        # logger.debug(f"Getting last state for session {session_id} with new session {new_session}")
        # if session_id and (not new_session or new_session.lower() == 'false'):
        #     creation_date_time = event.attributes['creation_date_time']
        #     last_state_creation_time = self.state_table.fetch(session_id, creation_date_time)

        return session_id, user_id, new_session, last_state_creation_time

    def get_state_attributes(self, user_utterance):
        state_attributes = {}
        state_attributes['creation_date_time'] = self.last_state_creation_time
        state_attributes['session_id'] = self.session_id
        state_attributes['user_id'] = self.user_id
        state_attributes['text'] = user_utterance
        state_attributes = {k: jsonpickle.encode(v) for k, v in state_attributes.items()}
        return state_attributes

    def get_user_attributes(self):
        user_attributes = self.user_table.fetch(self.user_id)
        user_attributes['user_id'] = self.user_id
        user_attributes['user_timezone'] = "Europe/London"
        user_attributes = {k: jsonpickle.encode(v) for k, v in user_attributes.items()}
        return user_attributes

    def get_last_state(self): # figure out new session and session_id
        if not self.new_session:
            last_state = self.state_table.fetch(self.session_id)
        else:
            last_state = None
        return last_state


def fixed_response(text, event, context):
    """
    Returns an apologetic response with a barebones state dictionary
    """
    try:
        conversation_id = event.get('session.attributes.conversationId')
    except KeyError:
        conversation_id = None
    state = {'conversation_id': conversation_id ,
            'session_id': event.get('session.sessionId'),
            'creation_date_time': str(datetime.datetime.utcnow().isoformat())}
    alexa_response = {
        'version': '1.0',
        'response': {
            'shouldEndSession': True,
            'outputSpeech': {
                'type': 'SSML',
                'ssml': f'<speak>{text}</speak>'
            },
            'reprompt': {
                'outputSpeech': {
                    'type': 'SSML',
                    'ssml': '''<speak>Hey, are you still there? If you want to continue
                        chatting, you can start by telling me what you want to talk about. Otherwise,
                        you can say stop at any time.</speak>'''
                }
            }
        },
        'sessionAttributes': {
            'creation_date_time': state['creation_date_time'],
            'conversationId': state['conversation_id']
        }
    }

    return alexa_response, state

