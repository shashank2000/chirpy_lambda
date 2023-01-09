from abc import ABC, abstractmethod
from dataclasses import dataclass 
from typing import List

from chirpy.core.camel.variable import Variable
from chirpy.core.camel.nlg import NLGNode
from chirpy.databases.databases import exists

@dataclass
class Predicate(ABC):
	@abstractmethod
	def evaluate(self, context):
		pass
		
funcs = {
	"IS_NONE": lambda x: x is None,
	"IS_TRUE": lambda x: bool(x),
	"IS_FALSE": lambda x: not bool(x),
}		
	
def get_func(verb):
	return funcs[verb]
	
def get_score(variable):
	if variable.namespace == 'Flags':
		return 2
	elif variable.namespace == 'State':
		return 1
	return 1
	
@dataclass
class VariablePredicate(Predicate):
	verb : str
	variable : Variable
	
	def evaluate(self, context):
		val = self.variable.generate(context)
		return get_func(self.verb)(val)
		
	def get_score(self):
		return get_score(self.variable)

@dataclass
class AndPredicate(Predicate):
	pred1 : Predicate
	pred2 : Predicate
	
	def evaluate(self, context):
		return self.pred1.evaluate(context) and self.pred2.evaluate(context)
		
	def get_score(self):
		return max(self.pred1.get_score(), self.pred2.get_score())
		
@dataclass
class OrPredicate(Predicate):
	pred1 : Predicate
	pred2 : Predicate
	
	def evaluate(self, context):
		return self.pred1.evaluate(context) or self.pred2.evaluate(context)
		
	def get_score(self):
		return max(self.pred1.get_score(), self.pred2.get_score())
		
@dataclass
class FalsePredicate(Predicate):
	def evaluate(self, context):
		return False
	def get_score(self):
		return 0
		
@dataclass
class TruePredicate(Predicate):
	def evaluate(self, context):
		return True 
		
	def get_score(self):
		return 0

@dataclass
class VariableIsPredicate(Predicate):
	variable : Variable
	val : NLGNode
	
	def evaluate(self, context):	
		return self.variable.generate(context) == self.val.generate(context)
		
	def get_score(self):
		return get_score(self.variable)
		
@dataclass
class VariableGTPredicate(Predicate):
	variable : Variable
	val : NLGNode
	
	def evaluate(self, context):	
		return self.variable.generate(context) > self.val.generate(context)
		
	def get_score(self):
		return get_score(self.variable)
				
				
@dataclass
class VariableLTPredicate(Predicate):
	variable : Variable
	val : NLGNode
	
	def evaluate(self, context):	
		return self.variable.generate(context) < self.val.generate(context)
		
	def get_score(self):
		return get_score(self.variable)
		
		
@dataclass 
class VariableInPredicate(Predicate):
	variable : Variable
	vals : List[NLGNode]
	
	def evaluate(self, context):
		var = self.variable.generate(context)
		for val in self.vals:
			if var == val.generate(context): return True
		return False
		
	def get_score(self):
		return get_score(self.variable)
		
@dataclass
class NotPredicate(Predicate):
	predicate : Predicate
	
	def evaluate(self, context):
		base = self.predicate.evaluate(context)
		return not base
	
	def get_score(self):
		return self.predicate.get_score()
		
@dataclass
class ExistsPredicate(Predicate):
	database_name : str
	database_key : NLGNode
	def evaluate(self, context):
		print("tok", self.database_name)
		return exists(self.database_name.generate(context), self.database_key.generate(context))

	def get_score(self):
		return 1.