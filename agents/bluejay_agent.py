import argparse
import logging
import uuid

# This needs to happen as early as possible for logging purposes
def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Setup"
    )
    parser.add_argument('-t', '--test_script', default="")
    parser.add_argument('-c', '--code', default=uuid.uuid4().hex)
    return parser

parser = init_argparse()
args = parser.parse_args()

try:
    from chirpy.core.logging_utils import setup_logger, update_logger, get_bluejay_logger_settings
except Exception as e:
    print("Error", e)
    raise e

logger = logging.getLogger('chirpylogger')
root_logger = logging.getLogger()
if not hasattr(root_logger, 'chirpy_handlers'):
    setup_logger(get_bluejay_logger_settings(code=args.code))
    


try:
    from collections import defaultdict
    
    import datetime
    import jsonpickle
    import os
    import uuid
    import time
    from typing import Dict
    import traceback
    
    from chirpy.annotators.corenlp import CorenlpModule
    from chirpy.annotators.navigational_intent.navigational_intent import NavigationalIntentModule
    from chirpy.annotators.stanfordnlp import StanfordnlpModule
    from chirpy.annotators.coref import CorefAnnotator
    from chirpy.annotators.emotion import EmotionAnnotator
    from chirpy.annotators.g2p import NeuralGraphemeToPhoneme
    from chirpy.annotators.gpt2ed import GPT2ED
    from chirpy.annotators.question import QuestionAnnotator
    from chirpy.annotators.blenderbot import BlenderBot
    import chirpy.core.flags as flags
    from chirpy.core.util import get_function_version_to_display
    from chirpy.annotators.dialogact import DialogActAnnotator
    from chirpy.core.entity_linker.entity_linker import EntityLinkerModule
    import chirpy.core.flags as flags
    from chirpy.core.latency import log_events_to_dynamodb, measure, clear_events
    from chirpy.core.regex.templates import StopTemplate
    from chirpy.core.handler import Handler
    
except Exception as e:
    logger.bluejay(f"Error: %s %s", exc_info=True, stack_info=True)
    raise e
    #exit()
import os
import sys

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

DEFAULT_REPROMPT = "Sorry, I don't think I understood. Could you repeat that please?".strip()

logger = logging.getLogger('chirpylogger')
apology_string = 'Sorry, I\'m having a really hard time right now. ' + \
'I have to go, but I hope you enjoyed our conversation so far. ' + \
'Have a good day!'

state_store = {}
user_store = defaultdict(dict)



class StateTable:
    def __init__(self):
        self.table_name = 'StateTable'

    def fetch(self, session_id, creation_date_time):
        #logger.warning(f"state_table fetching last state for session {session_id}, creation_date_time {creation_date_time} from table {self.table_name}")
        if session_id is None:
            return None
        try:
            item = None
            start_time = time.time()
            timeout = 2 #second
            while (item is None and time.time() < start_time + timeout):
                a = list(state_store.keys())[0]
                Q = '"'
                return state_store[(Q + session_id + Q, creation_date_time)]
            if item is None:
                #logger.error(
                #    f"Timed out when fetching last state\nfor session {session_id}, creation_date_time {creation_date_time} from table {self.table_name}.")
                pass
            else:
                return item
        except:
            logger.error("Exception when fetching last state")
            return None

    def persist(self, state: Dict):
        logger.primary_info('Using StateTable to persist state! Persisting to table {}'.format(self.table_name))
        logger.primary_info('session_id: {}'.format(state['session_id']))
        logger.primary_info('creation_date_time: {}'.format(state['creation_date_time']))
        
        try:
            assert 'session_id' in state
            assert 'creation_date_time' in state
            global state_store
            state_store[(state['session_id'], state['creation_date_time'])] = state
            return True
        except:
            logger.error("Exception when persisting state to table" + self.table_name, exc_info=True)
            return False

class UserTable():
    def __init__(self):
        self.table_name = 'UserTable'

    def fetch(self, user_id):
        logger.debug(
            f"user_table fetching last state for user {user_id} from table {self.table_name}")
        if user_id is None:
            return None
        try:
            item = None
            start_time = time.time()
            timeout = 2  # second
            while (item is None and time.time() < start_time + timeout):
                item = user_store[user_id]
            if item is None:
                logger.error(
                    f"Timed out when fetching user attributes\nfor user_id {user_id} from table {self.table_name}.")
            else:
                return item
        except:
            logger.error("Exception when fetching user attributes from table: " + self.table_name,
                         exc_info=True)
            return None

    def persist(self, user_attributes: Dict) -> None:
        """
        This will take the provided user_preferences object and persist it to DynamoDB. It does this by creating
                a dictionary representing the DynamoDB item to push consisting of user_id and a dictionary representing all of
                the user preferences.
        :param user_attributes: input UserAttributes object
        :return: None
        """
        try:
            assert 'user_id' in user_attributes
            global user_store
            user_store[user_attributes['user_id']] = user_attributes
            return True
        except:
            logger.error("Exception when persisting state to table: " + self.table_name, exc_info=True)
            return False

class LocalAgent():
    """
    Agent that inputs and outputs text, and runs callables locally.
    """
    def __init__(self):
        self.state_table = StateTable()
        self.user_table = UserTable()
        self.session_id = uuid.uuid4().hex
        self.user_id = "1"
        self.new_session = True
        self.last_state_creation_time = None

    def should_end_session(self, turn_result):
        return turn_result.should_end_session

    def should_launch():
        return True

    def get_state_attributes(self, user_utterance):
        state_attributes = {}
        state_attributes['creation_date_time'] = str(datetime.datetime.utcnow().isoformat())
        pipeline = os.environ.get('PIPELINE')
        state_attributes['pipeline'] = pipeline if pipeline is not None else ''
        commit_id = os.environ.get('COMMITID')
        state_attributes['commit_id'] = commit_id if commit_id is not None else ''
        state_attributes['session_id'] = self.session_id
        state_attributes['user_id'] = self.user_id
        state_attributes['text'] = user_utterance
        state_attributes = {k: jsonpickle.encode(v) for k, v in state_attributes.items()}
        return state_attributes

    def get_user_attributes(self):
        user_attributes = self.user_table.fetch(self.user_id)
        user_attributes['user_id'] = self.user_id
        user_attributes['user_timezone'] = None
        user_attributes = {k: jsonpickle.encode(v) for k, v in user_attributes.items()}
        return user_attributes

    def get_last_state(self): # figure out new session and session_id
        if not self.new_session:
            last_state = self.state_table.fetch(self.session_id, self.last_state_creation_time)
        else:
            last_state = None
        return last_state

    def create_handler(self):
        logger.warning(f"Annotator timeout is {NLP_PIPELINE_TIMEOUT}")
        return Handler(
            annotator_classes = [
                QuestionAnnotator,
                DialogActAnnotator,
                NavigationalIntentModule,
                StanfordnlpModule,
                CorenlpModule,
                EntityLinkerModule,
                BlenderBot
            ],
            annotator_timeout = NLP_PIPELINE_TIMEOUT
        )

    def process_utterance(self, user_utterance):

        # create handler (pass in RGs + annotators)
        handler = self.create_handler()

        current_state = self.get_state_attributes(user_utterance)
        user_attributes = self.get_user_attributes()
        last_state = self.get_last_state()

        turn_result = handler.execute(current_state, user_attributes, last_state)
        response = turn_result.response
        try:
            # create new state? -> what do we need here?
            if user_attributes != turn_result.user_attributes:
                self.user_table.persist(turn_result.user_attributes)
            self.state_table.persist(turn_result.current_state) # how do we get state?

        except:
            logger.error("Error persisting state")

        if self.new_session:
            self.new_session = False

        self.last_state_creation_time = current_state['creation_date_time']
        deserialized_current_state = {k: jsonpickle.decode(v) for k, v in turn_result.current_state.items()}

        return response, deserialized_current_state


from chirpy.core import flags



class RemoteNonPersistentAgent(LocalAgent):
    def __init__(self, session_id, user_id, new_session, last_state_creation_time):
        super().__init__()
        self.session_id = session_id
        self.user_id = user_id
        self.new_session = new_session
        self.last_state_creation_time = last_state_creation_time

def lambda_handler(args):
    if args.test_script:
        with open(args.test_script, 'r') as f:
            test_script = [x.strip() for x in f.readlines()]
    else:
        test_script = [""]
    local_agent = RemoteNonPersistentAgent('a', 'b', False, 0)
    user_input = ""
    while user_input != "bye":
        if len(test_script):
            user_input = test_script[0]
            test_script.pop(0)
            print('>', user_input)
        else:
            user_input = input('> ')
        logger.warning(f"received input {user_input}")
        try:
            logger.bluejay('before end turn')
            response, deserialized_current_state = local_agent.process_utterance(user_input)
            logger.bluejay('<<<END TURN>>>')
            print(response)
        except Exception as e:
            logger.bluejay(f"error: {traceback.format_exc()}", exc_info=True)
            logger.bluejay('<<<END TURN>>>')
            exit()


remote_url_config = {
    "corenlp": {
        "url": "http://localhost:4080"
    },
    "dialogact": {
        "url": "http://localhost:4081"
    },
    "g2p": {
        "url": "http://localhost:4082"
    },
    "gpt2ed": {
        "url": "http://localhost:4083"
    },
    "question": {
        "url": "http://localhost:4084"
    },
    "convpara": {
        "url": "http://localhost:4085"
    },
    "entitylinker": {
        "url": "http://localhost:4086"
    },
    "blenderbot": {
        "url": "http://localhost:4087"
    },
    "responseranker": {
        "url": "http://localhost:4088"
    },
    "stanfordnlp": {
        "url": "http://localhost:4089"
    },
    "infiller": {
        "url": "http://localhost:4090"
    }
}

# initializing environment variables for the session based off of remote config urls
for callable, config in remote_url_config.items():
    os.environ[f'{callable}_URL'] = config['url']



os.environ['ES_PORT'] = '443'
os.environ['ES_SCHEME'] = 'https'

lambda_handler(args)
