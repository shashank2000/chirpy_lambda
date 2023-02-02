import os
import random
import re

from agents.alexa.event import Event

import jsonpickle
import uuid

from agents.alexa.remote_alexa_agent import RemoteAlexaAgent

HAPPYBOT_ART_URL = "https://i.ibb.co/T0Xn1rq/Untitled-Artwork-3.jpg"
NEUTRALBOT_ART_URL = "https://i.ibb.co/1Xrjm7D/Untitled-Artwork-2.jpg"
BOT_ART_URLS = [HAPPYBOT_ART_URL, NEUTRALBOT_ART_URL]

# TODO: set the environment variables for invocations?
# these environment variables will be set in the lambda console, doing it here for now

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
    "question": {
        "url": "http://localhost:4084"
    },
    "entitylinker": {
        "url": "http://localhost:4086"
    },
    "blenderbot": {
        "url": "http://localhost:4087"
    },
    "stanfordnlp": {
        "url": "http://localhost:4089"
    }
}

def handler(event, context):
    print("in the handler!!")
    event = Event(event)

    user_utterance = event.get(path="request.intent.slots.text.value", default_val='')
    alexa_asr_user_utterance = convert_to_alexa_asr(user_utterance)

    agent = RemoteAlexaAgent(event)
    response, deserialized_current_state = agent.process_utterance(alexa_asr_user_utterance)

    BOT_ART_URL = random.choice(BOT_ART_URLS)

    # TODO(Ryan?): Consider returning the deserialized current state
    json_response = {
        "version": "1.0",
        "response": {
            "outputSpeech": {"type": "PlainText", "text": response},
            "card": {
                "type": "Standard",
                "title": "To quit, try 'Alexa, exit.'",
                "text": "Alexa Prize Socialbot Grand Challenge 5",
                "image": {
                    "largeImageUrl": BOT_ART_URL,
                    "smallImageUrl": BOT_ART_URL,
                },
            },
        },
    }
    return json_response

def convert_to_alexa_asr(sentence: str):
    alexa_asr_sentence = re.sub(r"[^\w\d'.\s]+", '', sentence) #remove punctuations except . and '
    alexa_asr_sentence = re.sub(r"(?P<pre>[\w\s\d]{2,})[.]+(?P<post>[\s]|$)", r'\g<pre> \g<post>', alexa_asr_sentence) #remove . except when they are used in an abbreviation (i.e. without space separation)
    alexa_asr_sentence = re.sub(r"(?P<pre>[\s])[.]+", r'\g<pre>', alexa_asr_sentence) #remove . except when they are used in an abbreviation (i.e. without space separation)
    alexa_asr_sentence = re.sub(r"[\s]+", " ", alexa_asr_sentence)
    alexa_asr_sentence = alexa_asr_sentence.lower().strip()
    return alexa_asr_sentence


