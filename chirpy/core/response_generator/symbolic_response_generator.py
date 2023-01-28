from chirpy.core.callables import NamedCallable
from chirpy.core.state_manager import StateManager
from chirpy.core.regex import response_lists
from chirpy.core.response_generator.response_type import *
from chirpy.core.response_generator.neural_helpers import (
    is_two_part,
    NEURAL_DECODE_CONFIG,
    get_random_fallback_neural_response,
)
from chirpy.core.response_generator.state import (
    NO_UPDATE,
    BaseSymbolicState,
    BaseSymbolicConditionalState,
)
from chirpy.core.response_generator.neural_helpers import (
    get_neural_fallback_handoff,
    neural_response_filtering,
)
from chirpy.core.response_generator.treelet import Treelet
from chirpy.core.response_generator_datatypes import (
    ResponseGeneratorResult,
    PromptResult,
    emptyResult,
    emptyResult_with_conditional_state,
    emptyPrompt,
    UpdateEntity,
    AnswerType,
)
from chirpy.core.response_generator.helpers import *
from chirpy.core.response_generator.response_generator import ResponseGenerator

from chirpy.core.camel.context import Context
from chirpy.core.camel.supernode import Supernode, SupernodeList

from chirpy.core.response_priority import ResponsePriority

from chirpy.symbolic_rgs import global_nlu
from chirpy.core.util import load_text_file
from typing import Set, Optional, List, Dict
import logging
import os

import json

from importlib import import_module

from concurrent import futures

from chirpy.core.entity_linker.entity_linker_classes import WikiEntity

logger = logging.getLogger("chirpylogger")

import os

STOPWORDS_FILEPATH = os.path.join(os.path.dirname(__file__), "../../data/long_stopwords.txt")
STOPWORDS = load_text_file(STOPWORDS_FILEPATH)


def get_supernode_paths():
    path = os.path.join(os.path.dirname(__file__), "../../symbolic_rgs/active_supernodes.list")
    with open(path, "r") as f:
        out = [x.strip() for x in f]
    out = [x for x in out if not x.startswith("#")]
    out = [x for x in out if x]
    return out


class SymbolicResponseGenerator:
    name = "SYMBOLIC_RESPONSE"

    def __init__(
        self,
        state_manager,
        supernode_paths=None,
    ):

        if supernode_paths is None:
            supernode_paths = get_supernode_paths()
        self.state_manager = state_manager
        self.supernodes = self.load_supernodes_from_paths(supernode_paths)
        if not self.state_manager.current_state.rg_state.turns_history:
            self.state_manager.current_state.rg_state.turns_history = self.get_initial_turns_history()

    def load_supernodes_from_paths(self, supernode_paths):
        output = {}
        for path in supernode_paths:
            output[path] = Supernode.load_from_path(path)
        return SupernodeList.from_paths(output)

    def get_supernodes(self):
        return self.supernodes.supernodes

    def get_next_supernode(self, context):
        return self.supernodes.select(context)

    def get_any_takeover_supernode(self, context, cancelled_supernodes):
        for supernode in self.get_supernodes():
            if supernode.name in cancelled_supernodes:
                continue
            if supernode.entry_conditions_takeover.evaluate(context, label=f"entry_conditions_takeover//{supernode.name}"):
                return supernode
        return self.supernodes["GLOBALS"]

    def get_current_supernode_with_fallback(self, context):
        """Returns the current supernode or GLOBALS (if no current supernode exists)."""
        logging.warning(f"Current supernode is {context.state.cur_supernode}.")
        path = context.state.cur_supernode or "GLOBALS"
        return self.supernodes[path]

    def get_takeover_or_current_supernode(self, context):
        """
        Returns a takeover supernode if one has high priority.
        Else, returns the current supernode if it exists.
        """
        for supernode in self.get_supernodes():
            logger.warning(f"Evaluating {supernode} for takeover {supernode.entry_conditions_takeover.evaluate(context)}")
            if (
                supernode.entry_conditions_takeover.evaluate(context)
                or supernode.entity_group_takeover(context)
            ):
                return supernode
        return self.get_current_supernode_with_fallback(context)

    def get_utilities(self, supernode):
        """Packages some useful data into one object."""

    def get_initial_turns_history(self):
        # This dictionary counts what turn number each supernode was last called
        # For each selected supernode, mark its last turn called as the current turn number
        return {supernode.name: 0 for supernode in self.get_supernodes()}

    def update_turns_history(self, state, supernode):
        assert supernode.name in state.turns_history
        state.turns_history[supernode.name] = self.state_manager.current_state.turn_num

    def update_context(self, update_dict, flags, state_update_dict):
        for value_name, value in update_dict.items():
            assert value_name.count(".") == 1, "Must have a namespace and a var name."
            namespace_name, value_name = value_name.split(".")
            assert namespace_name in [
                "flags",
                "state",
            ], f"Can't update namespace {namespace_name}"

            if namespace_name == "flags":
                flags[value_name] = value
            else:
                state_update_dict[value_name] = value

    def get_launch_supernode(self):
        return self.supernodes["LAUNCH"]

    def update_attributes(self, state, supernode, context):
        if supernode.details["can_only_prompt_once_for"]:
            variable = supernode.details["can_only_prompt_once_for"]
            generated_variable = variable.generate(context)
            if not generated_variable:
                # If no topic was found, we record None, so we won't go back
                # to this supernode if the person responds with another None response
                # during this current topic
                state.node_to_already_prompted[supernode.name].add(None)
                return
            ent_name = generated_variable.name
            state.node_to_already_prompted[supernode.name].add(ent_name)
            logger.warning(f"Can no longer prompt for: {state.node_to_already_prompted}")

    def get_response(self, state, utterance, kwargs=None) -> ResponseGeneratorResult:
        logger.warning("Begin response for SymbolicResponseGenerator.")
        if kwargs is None:
            kwargs = {}
        state.utterance = utterance
        if not self.state_manager.is_first_turn():
            context = Context.get_context(state, self.state_manager, kwargs=kwargs)
            supernode = self.get_takeover_or_current_supernode(context)
            logger.warning(f"We will continue with: {supernode}.")
            context = Context.get_context(state, self.state_manager, supernode, kwargs=kwargs)

            cancelled_supernodes = set()

            while not supernode.continue_conditions.evaluate(context):
                cancelled_supernodes.add(supernode.name)
                logger.warning(f"{supernode} can't continue, getting a takeover supernode")
                supernode = self.get_any_takeover_supernode(context, cancelled_supernodes)
                context = Context.get_context(state, self.state_manager, supernode)

            context.compute_locals()
            supernode.set_state.evaluate(context)

            tmp_helpers = supernode.nlg_helpers
            supernode.nlg_helpers = self.supernodes["GLOBALS"].nlg_helpers
            self.supernodes["GLOBALS"].locals.evaluate(context)
            supernode.nlg_helpers = tmp_helpers

            extra_subnodes = self.supernodes["GLOBALS"].subnodes if supernode.name != "GLOBALS" else None
            subnode, response = supernode.get_subnode_response(context, extra_subnodes=extra_subnodes)

            self.update_turns_history(state, supernode)
            self.update_attributes(state, supernode, context)
            context.utilities["response_text"] = response

            subnode.set_state.evaluate(context)

            supernode.set_state_after.evaluate(context)
            state.prev_flags = context.flags
            next_supernode = self.get_next_supernode(context)
            context.log_state()
        else:
            next_supernode = self.get_launch_supernode()
            response = ""

        context = Context.get_context(state, self.state_manager, next_supernode)
        context.compute_entry_locals()
        prompt = next_supernode.prompts.select(context)
        prompt_response = prompt.generate(context)
        prompt.assignments.evaluate(context)
        logger.primary_info(f"Received {prompt_response} from prompt {prompt}.")
        state.cur_supernode = next_supernode.name

        return ResponseGeneratorResult(
            text=response + prompt_response,
            priority=ResponsePriority.STRONG_CONTINUE,
            needs_prompt=False,
            state=state,
            cur_entity=None,
            answer_type=AnswerType.QUESTION_SELFHANDLING,
        )

    def update_state_if_chosen(self, state, conditional_state):
        if conditional_state is None:
            return state

        state.cur_supernode = conditional_state.cur_supernode
        state.data.update(conditional_state.data)

        return state

    def update_state_if_not_chosen(self, state, conditional_state):
        """
        By default, this sets the prev_treelet_str and next_treelet_str to '' and resets num_turns_in_rg to 0.
        Response types are also saved.
        No other attributes are updated.
        All other attributes in ConditionalState are set to NO-UPDATE
        """
        response_types = self.get_cache(f"{self.name}_response_types")
        if response_types is not None:
            state.response_types = construct_response_types_tuple(response_types)

        state.prev_treelet_str = ""
        state.next_treelet_str = ""
        state.num_turns_in_rg = 0

        return state

    def set_user_attribute(self, attr_name, value):
        setattr(self.state_manager.user_attributes, attr_name, value)

    def get_user_attribute(self, attr_name, default):
        return getattr(self.state_manager.user_attributes, attr_name, default)
