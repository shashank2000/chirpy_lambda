from dataclasses import dataclass, field
from typing import Any, List, Tuple, Set, Optional, Dict  # NOQA
from chirpy.symbolic_rgs import state_initialization
from chirpy.core.response_generator.response_type import ResponseType

import os
import logging

logger = logging.getLogger("chirpylogger")

"""
Define the base states that will be returned by all treelets.
Individual RGs should implement a state.py that defines their own State and ConditionalState 
that inherit from these classes.

For no update to be made, set the conditional state's attribute values to NO_UPDATE.
"""

NO_UPDATE = "no-update"

import yaml

BASE_PATH = os.path.join(os.path.dirname(__file__), "../../symbolic_rgs")
with open(os.path.join(BASE_PATH, "state.yaml")) as f:
    ALL_STATE_KEYS = yaml.safe_load(f)


@dataclass
class BaseState:
    prev_treelet_str: str = ""
    next_treelet_str: Optional[str] = ""
    response_types: Tuple[str] = ()
    num_turns_in_rg: int = 0


@dataclass
class BaseConditionalState:
    prev_treelet_str: str = ""
    next_treelet_str: Optional[str] = ""
    response_types: Tuple[str] = NO_UPDATE


def construct_response_types_tuple(response_types):
    return tuple([str(x) for x in response_types])


@dataclass
class BaseSymbolicState:
    prev_treelet_str: str = ""
    next_treelet_str: Optional[str] = ""
    response_types: Tuple[str] = ()
    num_turns_in_rg: int = 0
    cur_supernode: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    turns_history: Dict[str, int] = field(default_factory=dict)

    def __getitem__(self, key):
        assert key in ALL_STATE_KEYS, f"Not a valid key: {key}! (Did you add it to state.yaml?)"
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
        assert key in ALL_STATE_KEYS, f"Key not found: {key}"
        self.data[key] = new_value

    def __contains__(self, key, new_value):
        return key in ALL_STATE_KEYS

    def to_serializable(self):
        result = {}
        for k, v in self.data.items():
            result[k] = str(v)
        return result

    def update(self, data):
        for key in data:
            assert key in ALL_STATE_KEYS, f"Key not found: {key}"
        self.data.update(data)


@dataclass
class BaseSymbolicConditionalState:
    prev_treelet_str: str = ""
    next_treelet_str: Optional[str] = ""
    cur_supernode: str = NO_UPDATE
    response_types: Tuple[str] = NO_UPDATE
    data: Dict[str, Any] = NO_UPDATE
