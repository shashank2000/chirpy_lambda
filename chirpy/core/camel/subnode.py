from typing import List
from dataclasses import dataclass

from chirpy.core.camel.assignment import AssignmentList
from chirpy.core.camel.predicate import Predicate
from chirpy.core.camel.nlg import NLGNode

import json
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

	def select(self, context, all_possible_subnodes):
		possible_subnodes = [
			subnode for subnode in self.subnodes if subnode.entry_conditions.evaluate(context, label=f"subnode_entry_conditions//{subnode.name}")
		]
		if not len(possible_subnodes):
			return None

		all_possible_subnodes.extend(possible_subnodes)
		
		# return a possible subnode
		return random.choice(possible_subnodes)

@dataclass
class SubnodeList:
	groups : List[SubnodeGroup]
	
	def select(self, context):
		all_possible_subnodes = []
		subnodes = [group.select(context, all_possible_subnodes) for group in self.groups]
		possible_subnodes = [subnode for subnode in subnodes if subnode is not None]
		
		logger.primary_info(f"Possible subnodes are: {all_possible_subnodes}")
		logger.bluejay(f"subnodes: {json.dumps({node.name: {'available': True} for node in all_possible_subnodes})}")
		assert len(possible_subnodes), "No subnode found!"
		chosen_subnode = possible_subnodes[0]
		logger.bluejay(f"subnodes_chosen: {chosen_subnode.name}")

		# return the first possible subnode
		return chosen_subnode
