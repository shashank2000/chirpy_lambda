from typing import List
from dataclasses import dataclass

from chirpy.core.camel.assignment import AssignmentList
from chirpy.core.camel.predicate import Predicate
from chirpy.core.camel.nlg import NLGNode

import json

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
class SubnodeList:
	subnodes : List[Subnode]
	
	def select(self, context):
		possible_subnodes = [
			subnode for subnode in self.subnodes if subnode.entry_conditions.evaluate(context, label=f"subnode_entry_conditions//{subnode.name}")
		]
		logger.primary_info(f"Possible subnodes are: {possible_subnodes}")
		logger.bluejay(f"subnodes: {json.dumps({node.name: {'available': True} for node in possible_subnodes})}")
		assert len(possible_subnodes), "No subnode found!"
		logger.bluejay(f"subnodes_chosen: {possible_subnodes[0].name}")
		# for now, just return the first possible subnode
		return possible_subnodes[0]
