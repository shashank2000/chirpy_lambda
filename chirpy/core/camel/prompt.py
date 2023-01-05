from typing import List
from dataclasses import dataclass, field

from chirpy.core.camel.predicate import Predicate
from chirpy.core.camel.nlg import NLGNode
from chirpy.core.camel.assignment import AssignmentList

import random

@dataclass
class Prompt:
	name : str
	entry_conditions : Predicate
	response : NLGNode
	assignments : AssignmentList = field(default_factory=AssignmentList)
	
	def generate(self, context):
		return self.response.generate(context)

@dataclass
class PromptGroup:
	prompts : List[Prompt]

	def select(self, context):
		possible_prompts = [
			prompt for prompt in self.prompts if prompt.entry_conditions.evaluate(context)
		]
		if not len(possible_prompts):
			return None
		
		# return a possible prompt
		return random.choice(possible_prompts)

@dataclass
class PromptList:
	groups : List[PromptGroup]
	
	def select(self, context):
		prompts = [group.select(context) for group in self.groups]
		possible_prompts = [prompt for prompt in prompts if prompt is not None]
		assert len(possible_prompts), "No prompt found!"
		
		# return the first possible prompt
		return possible_prompts[0]
