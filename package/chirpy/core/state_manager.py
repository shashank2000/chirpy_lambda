from dataclasses import dataclass

import jsonpickle
import logging
from boto3.dynamodb.conditions import Key
from typing import List, Tuple, Optional # NOQA

from chirpy.core.user_attributes import UserAttributes
from chirpy.core.state import State
import chirpy.core.flags as flags
from chirpy.core.entity_tracker.entity_tracker import EntityTrackerState
from chirpy.core.util import print_dict_linebyline, get_ngrams
from chirpy.core.experiment import EXPERIMENT_PROBABILITIES, EXPERIMENT_NOT_FOUND


logger = logging.getLogger('chirpylogger')

@dataclass
class StateManager:
    current_state: State
    user_attributes: UserAttributes
    last_state: Optional[State] = None

    @property
    def last_state_active_rg(self):
        return self.last_state and self.last_state.active_rg

    @property
    def last_state_response(self):
        if not self.last_state: return None
        return self.last_state.rg_state.response
        
    def is_first_turn(self):
        return self.current_state.turn_num == 0
