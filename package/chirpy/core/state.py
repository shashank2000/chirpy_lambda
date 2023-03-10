from dataclasses import dataclass, field
from collections import defaultdict

import pytz
from typing import *
from datetime import datetime
import copy

from chirpy.core.entity_tracker.entity_tracker import EntityTrackerState
from chirpy.core.response_generator_datatypes import ResponseGeneratorResult
from chirpy.core.experiment import Experiments
from chirpy.core.flags import SIZE_THRESHOLD
from chirpy.core.util import print_dict_linebyline, get_ngrams
from chirpy.symbolic_rgs import state_initialization
import jsonpickle
import random
import logging

logger = logging.getLogger("chirpylogger")

# Set jsonpickle to always order keys alphabetically.
# ============================ Reason why we do this: ============================
# We jsonpickle python objects into strings and write them to the dynamodb StateTable.
# The jsonpickle strings might contain pointers (e.g. {"py/id": 3}) to objects within themselves.
# The pointers are relative to the ordering in the jsonpickled string.
# When we transfer the data from dynamodb StateTable to postgres, we turn the jsonpickled strings back into
# dictionaries. So in many cases, postgres contains pointers like {"py/id": 3} rather than the objects themselves.
# By making the order fixed (alphabetical), we can resolve the pointers and recover the data from postgres.
# ================================================================================
jsonpickle.set_encoder_options("simplejson", sort_keys=True)
jsonpickle.set_encoder_options("json", sort_keys=True)

import os
import yaml

BASE_PATH = os.path.join(os.path.dirname(__file__), "../symbolic_rgs")
with open(os.path.join(BASE_PATH, "state.yaml")) as f:
    ALL_STATE_KEYS = yaml.safe_load(f)


@dataclass
class BaseSymbolicState:
    prev_treelet_str: str = ""
    next_treelet_str: Optional[str] = ""
    response_types: Tuple[str] = ()
    num_turns_in_rg: int = 0
    cur_supernode: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    turns_history: Dict[str, int] = field(default_factory=dict)
    last_response: ResponseGeneratorResult = field(default_factory=lambda: None)
    node_to_already_prompted: DefaultDict[str, set] = field(default_factory=lambda: defaultdict(lambda: set()))
    prev_flags: DefaultDict[str, Any] = field(default_factory=dict)

    def check(self, key):
        assert key in ALL_STATE_KEYS, f"Key not found: {key}"

    def __getitem__(self, key):
        self.check(key)
        if key not in self.data:
            default_val = ALL_STATE_KEYS[key]
            if isinstance(default_val, str) and default_val.startswith("_"):
                func_name = default_val[1:]
                assert hasattr(state_initialization, func_name), f"{func_name} not found in state_initialization"
                func = getattr(state_initialization, func_name)
                default_val = func()
            self.data[key] = default_val
        return self.data[key]

    def __setitem__(self, key, new_value):
        self.check(key)
        self.data[key] = new_value

    def __contains__(self, key, new_value):
        return key in ALL_STATE_KEYS

    def update(self, data):
        for key in data:
            self.check(key)
        self.data.update(data)

    def to_serializable(self):
        result = {}
        for k, v in self.data.items():
            result[k] = str(v)
        return result


# @dataclass
# class BaseSymbolicConditionalState:
#     prev_treelet_str: str = ''
#     next_treelet_str: Optional[str] = ''
#     cur_supernode: str = NO_UPDATE
#     response_types: Tuple[str] = NO_UPDATE
#     data: Dict[str, Any] = NO_UPDATE


class State(object):
    """
    Encapsulates the current state of the Cobot system, as managed by the StateManager
    """

    def __init__(
        self,
        session_id: str,
        creation_date_time: str = None,
    ) -> None:
        """
        Initialize a State object with provided fields.
        :param user_id: user id
        :param conversation_id: conversation id
        :param session_id: session id
        :param creation_date_time: state creation timestamp, default to None
        :param request_type: LaunchRequest, IntentRequest, or SessionEndedRequest, default to None
        :param intent: NLU intent, default to None
        :param topic: topic, default to None
        :param asr: request from ASK lambda function
        :param text: text extracted from highest confidence asr or raw TEXT slot
        :param response: generated response
        """
        # self.user_id = user_id
        self.session_id = session_id
        if creation_date_time is not None:
            self.creation_date_time = creation_date_time
        else:
            self.creation_date_time = str(datetime.utcnow().isoformat())
        """
        TODO: pipeline & commit_id should go to agent
        storing commit_id as env variable so that we don't have to interface w/git
        """
        # A dictionary of experiment name to value of experiment variable
        self.history = []
        self.entity_tracker = EntityTrackerState()
        self.entity_tracker.init_for_new_turn()
        self.rg_state = BaseSymbolicState()
        self.turn_num = 0
        self.experiments = Experiments()
        self.cache = {}  # for caching data
        self.utterance = ""

    def update_from_last_state(self, last_state):
        self.history = last_state.history + [last_state.text, last_state.response]
        self.entity_tracker = copy.copy(last_state.entity_tracker)
        self.entity_tracker.init_for_new_turn()
        self.experiments = last_state.experiments
        self.rg_state = last_state.rg_state
        self.turn_num = last_state.turn_num + 1
        try:
            self.turns_since_last_active = last_state.turns_since_last_active
        except AttributeError:
            pass

    @property
    def active_rg(self):
        """
        Returns the active RG.

        Returns:
            If two different RGs supplied the response and prompt, return the prompting RG.
            If a single RG supplied both response and prompt, return that RG.
            If neither is set, return None
        """
        try:
            last_active_rg = self.selected_prompt_rg or self.selected_response_rg
        except AttributeError:
            try:
                last_active_rg = self.selected_response_rg
            except AttributeError:
                return None
        return last_active_rg

    def get_rg_state(self, rg_name: str):
        """
        Tries to get rg_name's RG state from current_state and return it.
        If unable to get it, logs an error message and returns None.
        """
        if not hasattr(self, "response_generator_states"):
            logger.error(
                f"Tried to get RG state for {rg_name} but current_state doesn't have attribute 'response_generator_states'"
            )
            return None
        rg_states = self.response_generator_states
        if rg_name not in rg_states:
            logger.error(
                f"Tried to get RG state for {rg_name}, but current_state.response_generator_states doesn't have a state for {rg_name}"
            )
            return None
        return rg_states[rg_name]

    def get_cache(self, key):
        return self.cache.get(key)

    def set_cache(self, key, value):
        self.cache[key] = value

    def serialize(self):
        logger.debug(f"Running jsonpickle version {jsonpickle.__version__}")
        logger.debug(f"jsonpickle backend names: {jsonpickle.backend.json._backend_names}")
        logger.debug(f"jsonpickle encoder options: {jsonpickle.backend.json._encoder_options}")
        logger.debug(f"jsonpickle fallthrough: {jsonpickle.backend.json._fallthrough}")

        # don't serialize cache
        encoded_dict = {k: jsonpickle.encode(v) for k, v in self.__dict__.items() if k != "cache"}
        total_size = sum(len(k) + len(v) for k, v in encoded_dict.items())
        if total_size > SIZE_THRESHOLD:
            logger.primary_info(
                f"Total encoded size of state is {total_size}, which is greater than allowed {SIZE_THRESHOLD}\n"
                f"Size of each value in the dictionary is:\n{print_dict_linebyline({k: len(v) for k, v in encoded_dict.items()})}"
            )

            # Tries to reduce size of the current state
            self.reduce_size()
            encoded_dict = {k: jsonpickle.encode(v) for k, v in self.__dict__.items()}
            total_size = sum(len(k) + len(v) for k, v in encoded_dict.items())
        logger.primary_info(
            f"Total encoded size of state is {total_size}\n"
            f"Size of each value in the dictionary is:\n{print_dict_linebyline({k: len(v) for k, v in encoded_dict.items()})}"
        )
        return encoded_dict

    @classmethod
    def deserialize(cls, mapping: dict):
        decoded_items = {}
        for k, v in mapping.items():
            try:
                decoded_items[k] = jsonpickle.decode(v)
            except:
                logger.error(f"Unable to decode {k}: {v} from past state")

        constructor_args = ["session_id", "creation_date_time"]
        base_self = cls(**{k: decoded_items.get(k, None) for k in constructor_args})

        for k in decoded_items:
            # if k not in constructor_args:
            setattr(base_self, k, decoded_items[k])
        return base_self

    @classmethod
    def deserialize_json(cls, mapping: dict):  # this method plays nicer w/ manually reconstructed states from past convos
        decoded_items = {}
        # logger.debug(mapping.items())
        for k, v in mapping.items():
            try:
                decoded_items[k] = v
            except:
                logger.error(f"Unable to decode {k}: {v} from past state")

        constructor_args = ["session_id", "creation_date_time"]
        base_self = cls(**{k: decoded_items.get(k, None) for k in constructor_args})

        for k in decoded_items:
            # if k not in constructor_args:
            setattr(base_self, k, decoded_items[k])
        return base_self

    def reduce_size(self):
        """
        Attribute specific size reduction
        """
        purgable_attributes = ["entity_linker", "entity_tracker", "response_results", "prompt_results"]
        objs = []

        logger.primary_info("Running reduce_size on the state object")
        # Collect all purgable objects from within lists and dicts
        for attr in purgable_attributes:
            try:
                attr = getattr(self, attr)
                if isinstance(attr, list):
                    objs += attr
                if isinstance(attr, dict):
                    objs += list(attr.values())
                else:
                    objs.append(attr)

            except AttributeError:
                logger.warning(f"State doesn't have purgable attribute {attr}")

        for obj in objs:
            if hasattr(obj, "reduce_size"):
                # The max_size is supposed to be per item, but it is hard to set it from here
                # because of interactions with other items. So setting an arbitrary size of
                # SIZE_THRESHOLD/8
                old_size = len(jsonpickle.encode(obj))
                obj.reduce_size(SIZE_THRESHOLD / 8)
                logger.primary_info(
                    f"object: {obj}'s encoded size reduced using reduce_size() from {old_size} to {len(jsonpickle.encode(obj))}"
                )
            else:
                logger.warning(f"There is no reduce_size() fn for object={obj}")

        # The reduce_size function is supposed to be in place, and hence we don't need to
        # set to explicitly put the purged objects back into lists and dicts

    def __str__(self):
        """
        Override the default string behavior
        :return: string representation
        """
        return str(self.serialize())

    # def __repr__(self):
    #     """
    #     Override the default string behavior
    #     :return: string representation
    #     """
    #     return self.__str__()
