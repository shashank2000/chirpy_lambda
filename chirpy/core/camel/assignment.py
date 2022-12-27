from typing import List
from dataclasses import dataclass, field

from chirpy.core.camel.variable import Variable
from chirpy.core.camel.nlg import NLGNode

@dataclass
class Assignment:
	variable : Variable
	value : NLGNode

@dataclass
class AssignmentList:
	assignments : List[Assignment] = field(default_factory=list)
	
	def evaluate(self, context):
		for assignment in self.assignments:
			context.set(assignment.variable, assignment.value.generate(context))
		