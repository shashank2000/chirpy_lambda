import os

from chirpy.core.camel.parser import parse
from chirpy.core.camel.predicate import Predicate, TruePredicate, FalsePredicate
from chirpy.core.camel.prompt import PromptList
from chirpy.core.camel.subnode import SubnodeList
from chirpy.core.camel.assignment import AssignmentList
from dataclasses import dataclass, field, fields
from typing import List, Any

from importlib import import_module

@dataclass
class Supernode:
	name : str
	subnodes : SubnodeList
	entry_conditions : Predicate = field(default_factory=TruePredicate)
	prompts : PromptList = field(default_factory=PromptList)
	continue_conditions : Predicate = field(default_factory=TruePredicate)
	locals : AssignmentList = field(default_factory=AssignmentList)
	entry_conditions_takeover : Predicate = field(default_factory=FalsePredicate)
	set_state : AssignmentList = field(default_factory=AssignmentList)
	set_state_after : AssignmentList = field(default_factory=AssignmentList)
	
	@classmethod
	def load(cls, camel_tree, name):
		initialization = {}
		for elem in camel_tree:
			key, item = elem
			assert any(field.name == key for field in fields(cls)), f"Section {key} not found, options are {[x.name for x in fields(cls)]}"
			initialization[key] = item
		supernode = cls(name=name, **initialization)
		
		return supernode
		
	def __post_init__(self):
		name = self.name
		self.nlu = import_module(f'chirpy.symbolic_rgs.{name}.nlu')
		self.nlg_helpers = import_module(f'chirpy.symbolic_rgs.{name}.nlg_helpers')		
		
	@classmethod
	def load_from_path(cls, path):
		BASE_PATH = os.path.join(os.path.dirname(__file__), '../../symbolic_rgs', path)
		with open(os.path.join(BASE_PATH, 'supernode.camel'), 'r') as f:
			camel_tree = parse(f.read())
		return cls.load(camel_tree, name=path)
		
	def get_flags(self, context):
		flags = self.nlu.get_flags(context)
		return flags
	
	def get_background_flags(self, context):
		# background_flags: flags to update even if this supernode was not chosen
		flags = self.nlu.get_background_flags(context)
		return flags		
		
	def __str__(self):
		return f"<{self.name}>"

	def __repr__(self):
		return f"<{self.name}>"
		
def __main__():
	from pprint import pprint
	BASE_PATH = os.path.dirname(__file__)
	with open(os.path.join(BASE_PATH, 'test1.camel'), 'r') as f:
		camel_tree = parse(f.read())
	supernode = Supernode.load(camel_tree, name='test1')
	pprint(supernode, width=200)
	
if __name__ == '__main__':
	__main__()
	
