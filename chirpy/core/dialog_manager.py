import copy
import logging
from typing import Dict, List, Optional

from chirpy.core.callables import run_multithreaded, ResponseGenerators
from chirpy.core.state_manager import StateManager
from chirpy.core.priority_ranking_strategy import PriorityRankingStrategy
from chirpy.core.flags import use_timeouts, inf_timeout
from chirpy.core.priority_ranking_strategy import RankedResults
from chirpy.core.response_generator_datatypes import ResponseGeneratorResult, PromptResult, UpdateEntity, CONTINUING_ANSWER_TYPES, is_killed
from chirpy.core.util import print_dict_linebyline, sentence_join
from chirpy.core.offensive_classifier.offensive_classifier import contains_offensive
from chirpy.response_generators.closing_confirmation.closing_confirmation_response_generator import CLOSING_CONFIRMATION_STOP
from chirpy.core.latency import measure


logger = logging.getLogger('chirpylogger')


class DialogManager:
    # These timeouts are in seconds
    INIT_STATE_TIMEOUT = 1 if use_timeouts else inf_timeout
    GET_ENTITY_TIMEOUT = 1 if use_timeouts else inf_timeout
    GET_RESPONSE_TIMEOUT = 7 if use_timeouts else inf_timeout
    GET_PROMPT_TIMEOUT = 1 if use_timeouts else inf_timeout
    UPDATE_STATE_TIMEOUT = None  # timeout for update_state_if_chosen and update_state_if_not_chosen fns
    # OFFENSIVE_TIMEOUT = 2 if use_timeouts else inf_timeout

    def __init__(self,
                 state_manager: StateManager,
                 ranking_strategy: PriorityRankingStrategy, 
                 ) -> None:
        self.state_manager = state_manager
        self.ranking_strategy = ranking_strategy
        from chirpy.core.response_generator.symbolic_response_generator import SymbolicResponseGenerator
        self.response_generator = SymbolicResponseGenerator(self.state_manager)


    @measure
    def execute_turn(self) -> (str, str, bool):
        """
        Execute one turn of dialogue.

        Returns:
            utterance: string (cannot be empty or None). The full utterance from Alexa.
            should_end_session: bool. Currently this is always False, but we might want to change it in the future
                e.g. if the user is being persistently offensive, talking about topics we aren't able to deal with,
                or the conversation is going really badly.
        """

        should_end_session = False
        logger.primary_info('Current state:\n{}'.format(print_dict_linebyline(self.state_manager.current_state.__dict__)),
                            extra={'color_lines_by_component': True})
        self.init_rg_state()  # Get RG states from last turn (or on first turn, run RGs' init_state fns)

        # Update the entity tracker state using the entity linker results
        self.update_entity_tracker_state()  # Update entity tracker's state

        logger.primary_info(f'Getting response...')
        
        state = self.state_manager.current_state.rg_state
        response = self.response_generator.get_response(state, self.state_manager.current_state.text)
        logger.warning(f"updated state is {response.state}")
        state.response = response.text

        # # Log final RG states
        # logger.primary_info('Final RG states at the end of this turn:\n{}'.format(
        #     print_dict_linebyline(self.state_manager.current_state.response_generator_states)),
        #     extra={'color_lines_by_component': True})

        return response.text, should_end_session

    def update_entity_tracker_state(self):
        """
        If the last active RG's get_entity function has an updated entity, update the entity tracker's state with it
        Else update entity tracker's state using default logic in entity tracker
        """

        # Get update_entity_result from last_active_rg
        last_active_rg = self.state_manager.last_state_active_rg  # str or None
        if last_active_rg:
            last_active_rg_state = copy.copy(self.state_manager.current_state.response_generator_states[last_active_rg])
            update_entity_results: Dict[str, UpdateEntity] = self.response_generators.run_multithreaded(
                rg_names=[last_active_rg],
                function_name='get_entity',
                args_list=[[last_active_rg_state, ]],
                timeout=DialogManager.GET_ENTITY_TIMEOUT)
            if update_entity_results and last_active_rg in update_entity_results:
                update_entity_result = update_entity_results[last_active_rg]
            else:
                logger.warning(
                    f"Failed or timed out while to running {last_active_rg}.get_entity. "
                    f"Skipping the RGs update to entity tracker")
                update_entity_result = UpdateEntity(False)
        else:
            update_entity_result = UpdateEntity(False)

        # Update the entity tracker, using update_entity_result if it has update=True
        if update_entity_result.update:
            logger.primary_info(f"Ran last_active_rg={last_active_rg}'s get_entity() function. It returned "
                                f"{update_entity_result}, so using this to update the entity tracker state",
                                extra={'color_msg_by_component': last_active_rg})
            self.state_manager.current_state.entity_tracker.update_from_rg(update_entity_result, last_active_rg, self.state_manager.current_state)
        else:
            if last_active_rg is not None:
                logger.primary_info(f"Ran last_active_rg={last_active_rg}'s get_entity() function. It returned "
                                    f"{update_entity_result}, so the entity tracker will update its state in the normal way",
                                    extra={'color_msg_by_component': last_active_rg})
            self.state_manager.current_state.entity_tracker.update_from_user(self.state_manager)


    def init_rg_state(self):
        """
        Initializes self.state_manager.current_state.response_generator_states, a dict from rg_name (str) to RG state.
        If it's the first turn of the conversation, run RGs' init_state fns.
        Otherwise get RG states from state_manager.last_state.
        """

        # If it's not the first turn, get RG states from last_state
        if self.state_manager.last_state:
            self.state_manager.current_state.rg_state = copy.copy(self.state_manager.last_state.rg_state)