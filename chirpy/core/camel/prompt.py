from typing import List
from dataclasses import dataclass, field

from chirpy.core.camel.predicate import Predicate
from chirpy.core.camel.nlg import NLGNode
from chirpy.core.camel.assignment import AssignmentList

import json
import random

import logging

logger = logging.getLogger("chirpylogger")


@dataclass
class Prompt:
    name: str
    entry_conditions: Predicate
    response: NLGNode
    assignments: AssignmentList = field(default_factory=AssignmentList)

    def generate(self, context):
        return self.response.generate(context)


@dataclass
class PromptGroup:
    prompts: List[Prompt]

    def select(self, context, all_possible_prompts):
        possible_prompts = [
            prompt
            for prompt in self.prompts
            if prompt.entry_conditions.evaluate(
                context, label=f"prompt_entry_conditions//{prompt.name}"
            )
        ]
        if not len(possible_prompts):
            return None

        all_possible_prompts.extend(possible_prompts)

        # return a possible subnode
        return random.choice(possible_prompts)


@dataclass
class PromptList:
    groups: List[PromptGroup]

    def select(self, context):
        all_possible_prompts = []
        prompts = [group.select(context, all_possible_prompts) for group in self.groups]
        possible_prompts = [prompt for prompt in prompts if prompt is not None]

        logger.primary_info(f"Possible prompts are: {all_possible_prompts}")
        logger.bluejay(
            f"prompts: {json.dumps({node.name: {'available': True} for node in all_possible_prompts})}"
        )
        assert len(possible_prompts), "No prompt found!"
        chosen_prompt = possible_prompts[0]
        logger.bluejay(f"prompts_chosen: {chosen_prompt.name}")

        # return the first possible prompt
        return chosen_prompt

    def __len__(self):
        return len(self.groups)
