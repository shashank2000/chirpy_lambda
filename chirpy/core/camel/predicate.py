from abc import ABC, abstractmethod
from dataclasses import dataclass 
from typing import List

from chirpy.core.camel.variable import Variable
from chirpy.core.camel.nlg import NLGNode


@dataclass
class Predicate(ABC):
	@abstractmethod
	def evaluate(self, python_context, contexts):
		pass
		
@dataclass
class VariablePredicate(Predicate):
	verb : str
	variable : Variable
	
	def evaluate(self, python_context, contexts):
		val = variable.generate()
		return get_func(self.verb)(val)

@dataclass
class AndPredicate(Predicate):
	pred1 : Predicate
	pred2 : Predicate
	
	def evaluate(self, python_context, contexts):
		return self.pred1.evaluate(python_context, contexts) and self.pred2.evaluate(python_context, contexts)
		
@dataclass
class OrPredicate(Predicate):
	pred1 : Predicate
	pred2 : Predicate
	
	def evaluate(self, python_context, contexts):
		return self.pred1.evaluate(python_context, contexts) or self.pred2.evaluate(python_context, contexts)
		
@dataclass
class FalsePredicate(Predicate):
	def evaluate(self, python_context, contexts):
		return False
		
@dataclass
class TruePredicate(Predicate):
	def evaluate(self, python_context, contexts):
		return False 

@dataclass
class VariableIsPredicate(Predicate):
	variable : Variable
	val : NLGNode
	
	def evaluate(self, python_context, contexts):	
		return self.variable.generate() == self.val.generate()
		
@dataclass 
class VariableInPredicate(Predicate):
	variable : Variable
	vals : List[NLGNode]
	def evaluate(self, python_context, contexts):
		var = self.variable.generate(python_context, contexts)
		for val in self.vals:
			if variable == val.generate(python_context, contexts): return True
		return False
		
@dataclass
class NotPredicate(Predicate):
	predicate : Predicate
	def evaluate(self, python_context, contexts):
		return not predicate.evaluate(python_context, contexts)
		

		
