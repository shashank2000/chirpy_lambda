import os
import re

from agents.alexa.event import Event

import jsonpickle
from flask import Flask, request
import uuid

#from agent.agents.remote_non_persistent import RemoteNonPersistentAgent as Agent
from agents.alexa.remote_alexa_agent import RemoteAlexaAgent
app = Flask(__name__)
from flask_cors import CORS
CORS(app, origins='*')

@app.route('/', methods=['POST'])
def conversational_turn():
    json_args = request.get_json(force=True)
    event = Event(json_args)

    user_utterance = event.get(path="request.intent.slots.text.value", default_val='')
    alexa_asr_user_utterance = convert_to_alexa_asr(user_utterance)

    agent = RemoteAlexaAgent(event)
    response, deserialized_current_state = agent.process_utterance(alexa_asr_user_utterance)

    #TODO: Consider returning the deserialized current state
    json_response = {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": response
            }
        }
    }
    return json_response

def convert_to_alexa_asr(sentence: str):
    alexa_asr_sentence = re.sub(r"[^\w\d'.\s]+", '', sentence) #remove punctuations except . and '
    alexa_asr_sentence = re.sub(r"(?P<pre>[\w\s\d]{2,})[.]+(?P<post>[\s]|$)", r'\g<pre> \g<post>', alexa_asr_sentence) #remove . except when they are used in an abbreviation (i.e. without space separation)
    alexa_asr_sentence = re.sub(r"(?P<pre>[\s])[.]+", r'\g<pre>', alexa_asr_sentence) #remove . except when they are used in an abbreviation (i.e. without space separation)
    alexa_asr_sentence = re.sub(r"[\s]+", " ", alexa_asr_sentence)
    alexa_asr_sentence = alexa_asr_sentence.lower().strip()
    return alexa_asr_sentence

if __name__ == '__main__':
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
        # "gpt2ed": {
        #     "url": "http://localhost:4083"
        # },
        "question": {
            "url": "http://localhost:4084"
        },
        "entitylinker": {
            "url": "http://localhost:4086"
        },
        "blenderbot": {
            "url": "http://localhost:4087"
        },
        # "responseranker": {
        #     "url": "http://localhost:4088"
        # },
        "stanfordnlp": {
            "url": "http://localhost:4089"
        },
        # "infiller": {
        #     "url": "WILL HARDCODE THIS" # TODO (eric): REPLACE THIS WITH SOMETHING MEANINGFUL
        # } if args.use_colbert else { # chirpy2022 project
        #     "url": "http://localhost:4090"
        # }
    }

    # initializing environment variables for the session based off of remote config urls
    for callable, config in remote_url_config.items():
        os.environ[f'{callable}_URL'] = config['url']
    print(f"{os.environ.get('blenderbot_URL', 'oh no')}")

    os.environ['ES_PORT'] = '443'
    os.environ['ES_SCHEME'] = 'https'
    app.run(host="127.0.0.1", port=5001)



