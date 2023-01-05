from typing import List
from dataclasses import dataclass

from chirpy.core.camel.assignment import AssignmentList
from chirpy.core.camel.predicate import Predicate
from chirpy.core.camel.nlg import NLGNode

import random
import logging
logger = logging.getLogger('chirpylogger')

@dataclass
class Subnode:
	name : str
	entry_conditions : Predicate
	response : NLGNode
	set_state : AssignmentList
	
	def generate(self, context):
		logger.primary_info(f"Subnode {self.name} is generating.")
		return self.response.generate(context)
		
	def __str__(self):
		return "<<" + self.name + ">>"
		
	def __repr__(self):
		return self.__str__()

@dataclass
class SubnodeGroup:
	subnodes : List[Subnode]

	def select(self, context):
		possible_subnodes = [
			subnode for subnode in self.subnodes if subnode.entry_conditions.evaluate(context)
		]
		if not len(possible_subnodes):
			return None
		
		# return a possible subnode
		return random.choice(possible_subnodes)

@dataclass
class SubnodeList:
	groups : List[SubnodeGroup]
	
	def select(self, context):
		subnodes = [group.select(context) for group in self.groups]
		possible_subnodes = [subnode for subnode in subnodes if subnode is not None]
		logger.primary_info(f"Possible subnodes are: {possible_subnodes}")
		assert len(possible_subnodes), "No subnode found!"

		# return the first possible subnode
		return possible_subnodes[0]
