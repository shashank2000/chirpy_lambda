from typing import List
from dataclasses import dataclass

from chirpy.core.camel.assignment import AssignmentList
from chirpy.core.camel.predicate import Predicate
from chirpy.core.camel.nlg import NLGNode

import logging
logger = logging.getLogger('chirpylogger')

@dataclass
class Subnode:
	name : str
	entry_conditions : Predicate
	response : NLGNode
	set_state : AssignmentList
	
	def generate(self, context):
		return self.response.generate(context)
	
@dataclass
class SubnodeList:
	subnodes : List[Subnode]
	
	def select(self, context):
		possible_subnodes = [
			subnode for subnode in self.subnodes if subnode.entry_conditions.evaluate(context)
		]
		assert len(possible_subnodes), "No subnode found!"
		# for now, just return the first possible subnode
		return possible_subnodes[0]
