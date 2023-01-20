import logging
import requests
from injector import singleton
from typing import Optional, Dict, Any, Union
from chirpy.core.latency import measure
from chirpy.core.flags import use_timeouts, inf_timeout
from chirpy.core.regex.templates import StopTemplate
import json

logger = logging.getLogger('chirpylogger')

GET_TIMEZONE_TIMEOUT = 0.25 if use_timeouts else inf_timeout  # timeout in seconds for fetching user's timezone

from typing import Optional, Any, Union, Dict


class PathDict(object):
    """
    Wrap a dictionary and provide function to get nested item using a string path.
    """

    def __init__(self, init_data: dict) -> None:
        self._data = init_data
        logger.debug(f"Received the following initialization data for PathDict: {json.dumps(init_data, indent=2)}")

    def get(self,
            path: str,
            default_val: Optional[Any] = None
            ) -> Union[Optional[Any], Dict[Any, Any]]:
        """
        Given a string path, return nested value. If the string path is invalid, return default value.
        :param path: A string path separated by period. EX: 'request.intent.name'
        :return A nested item, if the path is valid. Or a default value, if the path is invalid.
        """
        key_list = path.split('.')
        cur: Union[Optional[Any], Dict[Any, Any]] = self._data
        for key in key_list:
            if isinstance(cur, dict) and key in cur:
                cur = cur.get(key)
            else:
                cur = default_val
                break
        return cur

    @property
    def source(self) -> dict:
        """
        Return original dictionary object
        """
        return self._data


@singleton
class Event(PathDict):
    """
    Use `PathDict` to wrap event parameters from lambda handler function.
    Provide shortcut functions to fetch some specific data from the event.
    """

    @property
    def app_id(self) -> str:
        app_id = self.get('context.System.application.applicationId')
        if app_id is None:
            app_id = self.get('session.application.applicationId')
        if app_id is None:
            app_id = ''
        if not isinstance(app_id, str):
            raise TypeError("app_id should be a str")
        return app_id

    @property
    def user_id(self) -> str:
        user_id = self.get('context.System.user.userId')
        if user_id is None:
            user_id = self.get('session.user.userId')
        if user_id is None:
            user_id = ''
        if not isinstance(user_id, str):
            raise TypeError("user_id should be a str")
        return user_id

    @property
    def conversation_id(self) -> Union[str, None]:
        conversation_id = self.get('request.payload.conversationId')
        logger.primary_info(f"Conversation id: {conversation_id}")
        if conversation_id is None:
            conversation_id = self.get('session.attributes.conversationId')
            if isinstance(conversation_id, str):
                conversation_id = conversation_id.strip('\\"')
            if conversation_id == 'null':
                conversation_id = None
        if conversation_id is not None:
            if not isinstance(conversation_id, str):
                raise TypeError("conversation_id should be a str or None")
        return conversation_id

    @property
    def attributes(self) -> dict:
        attributes_ =  self.get('session.attributes', {})
        if not isinstance(attributes_, dict):
            raise TypeError("attributes should be a dict")
        return attributes_

    @property
    def speech_recognition(self) -> list:
        speech_recognition = self.get('request.payload.speechRecognition.hypotheses')
        if speech_recognition is None:
            speech_recognition = self.get('request.speechRecognition.hypotheses')
        if speech_recognition is None:
            speech_recognition = []
        if not isinstance(speech_recognition, list):
            raise TypeError("speech_recognition should be a list")
        return speech_recognition

    @measure
    def get_user_timezone(self) -> Optional[str]:
        """
        Get the user timezone from the Alexa customer settings API.
        https://developer.amazon.com/en-US/docs/alexa/smapi/alexa-settings-api-reference.html
        Returns a string e.g. 'America/New_York'.
        If we are unable to get the user's timezone (which will always happen if the conversation is NOT happening
        on an Alexa device, so this includes interactive mode, integration tests etc), returns None.
        If we are unable to get the user's timezone but this IS a user conversation (i.e. conversation_id is not
        None), additionally logs an error.
        """
        # Get deviceId, apiEndpoint and apiAccessToken
        deviceId = self.get('context.System.device.deviceId')
        if deviceId is None:
            logger.info('Unable to get device_id from event, so unable to get user timezone')
        apiEndpoint = self.get('context.System.apiEndpoint')
        if apiEndpoint is None:
            logger.info('Unable to get apiEndpoint from event, so unable to get user timezone')
        apiAccessToken = self.get('context.System.apiAccessToken')
        if apiAccessToken is None:
            logger.info('Unable to get apiAccessToken from event, so unable to get user timezone')

        # If we couldn't get them, log and return None
        if not (deviceId and apiEndpoint and apiAccessToken):
            if self.conversation_id:
                logger.error('conversation_id is not None, but we were unable to get deviceId/apiEndpoint/apiAccessToken')
            logger.warning(f'Unable to get deviceId/apiEndpoint/apiAccessToken, so setting user timezone as None')
            return None

        # Try to get the timezone from the API
        try:
            url = apiEndpoint + '/v2/devices/{deviceId}/settings/System.timeZone'.format(deviceId=deviceId)
            headers = {'Authorization': 'Bearer {}'.format(apiAccessToken)}
            logger.info(f'Sending request to get user timezone to this url: {url} with these headers: {headers}')
            r = requests.get(url=url, headers=headers, timeout=GET_TIMEZONE_TIMEOUT)
            logger.info(f'Received this response: {r}')

            # If the response has an error code, raise the readable error
            if not r.ok:
                r.raise_for_status()

            # If the API returned "no setting exists", log warning and return None
            if r.status_code == 204:
                logger.warning('Tried to get user timezone, but Alexa customer settings API returned 204 (No setting value exists), so setting as None')
                return None

            output = r.json()
            logger.info(f'Received this output: {output}')
            return output
        except requests.exceptions.Timeout as e:
            logger.warning(f'Timed out when getting user timezone with timeout = {GET_TIMEZONE_TIMEOUT} seconds')  # don't include stack trace for timeouts
        except:
            logger.error('Error when trying to get user timezone, so returning None.', exc_info=True)
            return None

    def should_launch(self):
        """
        Determines if we should launch a new conversation
        """
        request_type = self.get('request.type', None) # standardize request type
        if request_type == 'LaunchRequest':
            return True
        return False


    def should_end_session(self):
        """Determines whether we should immediately end the conversation, rather than running the bot"""
        if self.get('request_type') == 'SessionEndedRequest':
            logger.primary_info('Received event with request_type SessionEndedRequest, so ending conversation')
            return True
        elif self.get('request.intent.name') in ['AMAZON.StopIntent', 'AMAZON.CancelIntent']:
            logger.primary_info(f"Received event with intent {self.get('request.intent.name')}, so ending conversation")
            return True
        else:
            return False

    def extract_text(self):
        """
        Returns text, which is a string (might be empty).
        - First we try to get text from request.intent.slots.text.value.
        - If it can't be found there, we instead get it by putting the top-1 ASR transcription tokens together.
        - We prefer request.intent.slots.text.value to the ASR tokens because it sometimes has fixes applied (e.g.
        we have 'i. b. m.' in asr tokens and 'ibm' in slot text).
        """
        # Get text_from_slots (either string or None)
        try:
            text_from_slots = self.get('request.intent.slots.text.value').strip().lower()
        except:
            logger.debug(f'Could not find request.intent.slots.text.value in event {self}. Will use text_from_asr instead.')
            text_from_slots = None

        # Get text_from_asr (either string or None)
        asr_texts = []
        if self.get('speechRecognition') is not None:
            for transcription in self.get('speechRecognition'):
                text = ' '.join([token['value'] for token in transcription['tokens']])
                asr_texts.append(text)
        if len(asr_texts) > 0:
            logger.debug(f'Got {len(asr_texts)} ASR transcriptions: {asr_texts}')
            text_from_asr = asr_texts[0].strip()
        else:
            logger.debug(f'Did not get any ASR texts from event {self}. Setting text_from_asr to None.')
            text_from_asr = None

        # If we have text_from_slots, use it. Otherwise if we have text_from_asr, use it. Otherwise return empty string.
        if text_from_slots is not None:
            if text_from_slots != text_from_asr:
                logger.debug(f'text_from_slots="{text_from_slots}" does not match text_from_asr="{text_from_asr}". '
                             f'We will use text_from_slots, as it often has certain fixes in place (e.g. transform '
                             f'acronyms from "i. b. m." to "ibm").')
            return text_from_slots
        elif text_from_asr is not None:
            return text_from_asr
        else:
            logger.debug('Both text_from_slots and text_from_asr are None, so returning text="".')
            return ''

    def get_state_attributes(self):
        """
        Initialize current_state from Event
        :param event: ASK event
        """
        state_attributes = {}
        state_attributes['asr'] = self.get('request.speechRecognition')
        state_attributes['text'] = self.extract_text()
        state_attributes['session_id'] = self.get('session.sessionId')  # self.user_attributes['session_id']
        return state_attributes