import os

from lark import Lark, Transformer, Token, Tree
from chirpy.core.camel import nlg, predicate, variable, prompt, assignment, subnode

import sys

BASE_PATH = os.path.dirname(__file__)

with open(os.path.join(BASE_PATH, 'grammar.lark'), 'r') as f:
	grammar = f.read()
	
import logging
logger = logging.getLogger('chirpylogger')
	
class SupernodeMaker(Transformer):
	def variable(self, tok): return variable.Variable(str(tok[0]), str(tok[1]))
	
	def nlg__variable(self, tok): return self.variable(tok)
	def condition__variable(self, tok): return self.variable(tok)
	
	def condition__bool(self, tok):
		if str(tok[0]).lower() == 'true':
			return predicate.TruePredicate()
		return predicate.FalsePredicate()
	
	def condition__predicate(self, tok):
		if str(tok[0]) == 'IS_EQUAL':
			return predicate.VariableIsPredicate(variable=tok[1], val=tok[2])
		elif str(tok[0]) == 'IS_IN': 
			return predicate.VariableInPredicate(variable=tok[1], vals=tok[2:])
		elif str(tok[0]) == 'IS_GREATER_THAN': 
			return predicate.VariableGTPredicate(variable=tok[1], val=tok[2])
		elif str(tok[0]) == 'IS_LESS_THAN': 
			return predicate.VariableLTPredicate(variable=tok[1], val=tok[2])
		elif str(tok[0]) == 'EXISTS':
			return predicate.ExistsPredicate(database_name=tok[1], database_key=tok[2])
		else:
			return predicate.VariablePredicate(verb=str(tok[0]), variable=tok[1])
	
	def condition(self, tok):
		if isinstance(tok, list):
			if len(tok) == 1: return tok[0]
			if isinstance(tok[0], Token) and tok[0].type == 'condition__OP':
				return tok[1]
			# condition "and" condition
			if isinstance(tok[1], Token) and tok[1] == 'and':
				return predicate.AndPredicate(tok[0], tok[2])
			if isinstance(tok[1], Token) and tok[1] == 'or':
				return predicate.OrPredicate(tok[0], tok[2])
		return tok
		
	def unary(self, tok):
		if isinstance(tok[0], Token) and tok[0].type == 'condition__NOT':
			return predicate.NotPredicate(tok[1])
		assert False
	
	def entry_conditions_section(self, tok):
		if len(tok):
			return "entry_conditions", tok[0]
		return None
		
	## NLG
	
	def nlg__ESCAPED_STRING(self, tok): return nlg.String(str(tok.value)[1:-1])

	def condition__ESCAPED_STRING(self, tok): return self.nlg__ESCAPED_STRING(tok)

	def nlg__PUNCTUATION(self, tok): return nlg.String(str(tok.value))
	def nlg__val(self, tok): 
		operations = []
		if len(tok) > 1:
			# tokens are [operator, pipe function, operator, pipe function, ...]
			extra_args = tok[1:]
			iterator = iter(extra_args)
			# pairs extra_args into [(operator, pipe function), (operator, pipe function), ...]
			operations = list(zip(iterator, iterator))
			operations = [(op[0].value, op[1].value) for op in operations]
		return nlg.Val(tok[0], operations)
	def nlg__neural_generation(self, tok): return nlg.NeuralGeneration(tok[0])
	def nlg__one_of(self, tok): 
		return nlg.OneOf(tok)
	def nlg__constant(self, tok): return nlg.Constant(tok[0].value)
	
	def nlg__inflect(self, tok): return nlg.Inflect(tok[0], tok[1])
	def nlg__inflect_engine(self, tok): return nlg.InflectEngine(tok[0], tok[1])

	def nlg__lookup(self, tok): return nlg.DatabaseLookup(tok[0], tok[1], tok[2])
	def nlg__STRING(self, tok): return tok
	def nlg__helper(self, tok):
		func_name = tok[0].value
		args = tok[1:]
		return nlg.NLGHelper(func_name, args)
	def nlg(self, tok):
		if isinstance(tok, list):
			if len(tok) == 1: return tok[0]
			return nlg.NLGList(tok)
		return tok
	def condition__nlg(self, tok): return self.nlg(tok)

	def prompt_group(self, tok):
		return prompt.PromptGroup(tok)
	
	def prompt(self, tok):
		prompt_name = tok[0].value
		condition = predicate.TruePredicate()
		assignment_list = []
		response = None
		for token in tok[1:]:
			if isinstance(token, predicate.Predicate):
				condition = token
			elif isinstance(token, nlg.NLGNode):
				response = token
			elif isinstance(token, assignment.Assignment):
				assignment_list.append(token)
		return prompt.Prompt(
			name=prompt_name,
			entry_conditions=condition,
			response=response,
			assignments=assignment.AssignmentList(assignment_list)
		)
	
	def subnode_group(self, tok):
		return prompt.PromptGroup(tok)
		
	def subnode(self, tok):
		subnode_name = tok[0].value
		condition = predicate.TruePredicate()
		assignment_list = []
		response = None
		for token in tok[1:]:
			if isinstance(token, predicate.Predicate):
				condition = token
			elif isinstance(token, nlg.NLGNode):
				response = token
			elif isinstance(token, assignment.Assignment):
				assignment_list.append(token)
		return subnode.Subnode(
			name=subnode_name,
			entry_conditions=condition,
			response=response,
			set_state=assignment.AssignmentList(assignment_list)
		)
	
	def continue_conditions_section(self, tok):
		return tok
		
	def assignment(self, tok):
		return assignment.Assignment(tok[0], tok[1])
	
	def condition_assignment(self, tok):
		return assignment.Assignment(tok[0], tok[1], True)

	### ENTRY LOCALS
	def entry_locals_section(self, tok):
		return "entry_locals", assignment.AssignmentList(tok)
		
	### PROMPT
	def prompt_section(self, tok):
		if len(tok):
			return "prompts", prompt.PromptList(tok)
		return None
		
	### CONTINUE CONDITIONS
	def continue_conditions_section(self, tok):
		return "continue_conditions", tok[0]
		
	### LOCALS
	def locals_section(self, tok):
		return "locals", assignment.AssignmentList(tok)
		
	### ENTRY CONDITIONS TAKEOVER
	def entry_conditions_takeover_section(self, tok):
		return "entry_conditions_takeover", tok[0]
		
	### SET STATE
	def set_state_section(self, tok):
		return "set_state", assignment.AssignmentList(tok)
		
	### SUBNODE
	def subnodes_section(self, tok):
		return "subnodes", subnode.SubnodeList(tok)
		
	### SET STATE AFTER
	def set_state_after_section(self, tok):
		return "set_state_after", assignment.AssignmentList(tok)
	
	def document(self, tok):
		return tok
		
	def __getattr__(self, attr):
		if attr.startswith('condition__') and hasattr(self, attr.replace('condition__', '')):
			return getattr(self, attr.replace('condition__', ''))
		return super().__getattr__(self, attr)
		

def nice_error(e):
	sys.tracebacklimit = 1
	raise e

parser = Lark(grammar, start='document', parser='lalr', transformer=SupernodeMaker(), import_paths=[BASE_PATH])
def parse(text):
	return parser.parse(text, on_error=nice_error)