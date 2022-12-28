from typing import List
from dataclasses import dataclass, field

from chirpy.core.camel.predicate import Predicate
from chirpy.core.camel.nlg import NLGNode
from chirpy.core.camel.assignment import AssignmentList

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
			prompt for prompt in self.prompts if prompt.entry_conditions.evaluate(context)
		]
		assert len(possible_prompts), "No prompt found!"
		
		# for now, just return the first possible subnode
		return possible_prompts[0]
