from typing import List
from dataclasses import dataclass, field
import json

from chirpy.core.camel.predicate import Predicate
from chirpy.core.camel.nlg import NLGNode
from chirpy.core.camel.assignment import AssignmentList

import logging
logger = logging.getLogger('chirpylogger')

@dataclass
class Prompt:
	name : str
	entry_conditions : Predicate
	response : NLGNode
	assignments : AssignmentList = field(default_factory=AssignmentList)
	
	def generate(self, context):
		return self.response.generate(context)

@dataclass
class PromptList:
	prompts : List[Prompt]
	
	def select(self, context):
		possible_prompts = [
			prompt for prompt in self.prompts if prompt.entry_conditions.evaluate(context, label=f"prompt_entry_conditions//{prompt.name}")
		]
		logger.primary_info(f"Possible prompts are: {possible_prompts}")
		logger.bluejay(f"prompts: {json.dumps({node.name: {'available': True} for node in possible_prompts})}")
		assert len(possible_prompts), "No prompt found!"
		logger.bluejay(f"prompts_chosen: {possible_prompts[0].name}")
		# for now, just return the first possible prompt
		return possible_prompts[0]