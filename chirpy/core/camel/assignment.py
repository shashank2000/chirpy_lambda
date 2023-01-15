from typing import List, Union
from dataclasses import dataclass, field

from chirpy.core.camel.variable import Variable
from chirpy.core.camel.nlg import NLGNode, Key
from chirpy.core.camel.predicate import Predicate

@dataclass
class Assignment:
	variable : Variable
	keys : List[Key]
	value : Union[NLGNode, Predicate]

@dataclass
class AssignmentList:
	assignments : List[Assignment] = field(default_factory=list)
	
	def evaluate(self, context):
		for assignment in self.assignments:
			context.setDictionary(assignment.variable, assignment.keys, assignment.value.generate(context))
		