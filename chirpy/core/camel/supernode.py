import os

from chirpy.core.camel.parser import parse
from chirpy.core.camel.predicate import Predicate, TruePredicate, FalsePredicate
from chirpy.core.camel.prompt import PromptList
from chirpy.core.camel.subnode import SubnodeList
from chirpy.core.camel.assignment import AssignmentList
from dataclasses import dataclass, field, fields
from typing import List, Any

@dataclass
class Supernode:
	subnodes : SubnodeList
	entry_conditions : Predicate = field(default_factory=TruePredicate)
	prompts : PromptList = field(default_factory=PromptList)
	continue_conditions : Predicate = field(default_factory=TruePredicate)
	locals : AssignmentList = field(default_factory=AssignmentList)
	entry_conditions_takeover : Predicate = field(default_factory=FalsePredicate)
	set_state : AssignmentList = field(default_factory=AssignmentList)
	set_state_after : AssignmentList = field(default_factory=AssignmentList)
	
	@classmethod
	def load(cls, camel_tree):
		initialization = {}
		#print(camel_tree)
		for elem in camel_tree:
			key, item = elem
			assert any(field.name == key for field in fields(cls)), f"Section {key} not found, options are {[x.name for x in fields(cls)]}"
			initialization[key] = item
		supernode = cls(**initialization)
		return supernode
		
def __main__():
	from pprint import pprint
	BASE_PATH = os.path.dirname(__file__)
	with open(os.path.join(BASE_PATH, 'test1.camel'), 'r') as f:
		camel_tree = parse(f.read())
	supernode = Supernode.load(camel_tree)
	pprint(supernode, width=200)
	
if __name__ == '__main__':
	__main__()
	
