from typing import List
from dataclasses import dataclass

from chirpy.core.camel.variable import Variable
from chirpy.core.camel.nlg import NLGNode

@dataclass
class Assignment:
	variable : Variable
	value : NLGNode

@dataclass
class AssignmentList:
	assignments : List[Assignment]

