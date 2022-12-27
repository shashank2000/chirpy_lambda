import os

from lark import Lark, Transformer, Token, Tree
from chirpy.core.camel import nlg, predicate, variable, prompt, assignment, subnode

BASE_PATH = os.path.dirname(__file__)

with open(os.path.join(BASE_PATH, 'grammar.lark'), 'r') as f:
	grammar = f.read()
	
class SupernodeMaker(Transformer):
	def variable(self, tok): return variable.Variable(str(tok[0]), str(tok[1]))
	
	def nlg__variable(self, tok): return self.variable(tok)
	def condition__variable(self, tok): return self.variable(tok)
	
	def condition__predicate(self, tok): return predicate.VariablePredicate(verb=str(tok[0]), variable=tok[1])
	
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
	
	def entry_conditions_section(self, tok):
		if len(tok):
			return "entry_conditions", tok[0]
		return None
		
	## NLG
	
	def nlg__ESCAPED_STRING(self, tok): return str(tok.value)[1:-1]
	def nlg__PUNCTUATION(self, tok): return str(tok.value)
	def nlg__val(self, tok): return tok[0]
	def nlg__neural_generation(self, tok): return nlg.NeuralGeneration(tok[0])
	def nlg__one_of(self, tok): return nlg.OneOf(tok[1])
	def nlg__constant(self, tok): return nlg.Constant(tok[0].value)
	def nlg__inflect(self, tok): return nlg.Inflect(tok[0], tok[1])
	def nlg__inflect_engine(self, tok): return nlg.Inflect(tok[0], tok[1])
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
	
	def prompt(self, tok):
		if len(tok) == 3:
			prompt_name, condition, nlg = tok
		else:
			prompt_name, nlg = tok
			condition = predicate.TruePredicate()
		return prompt.Prompt(prompt_name.value, condition, nlg)
		
	def subnode(self, tok):
		if len(tok) == 3:
			subnode_name, condition, nlg = tok
		else:
			subnode_name, nlg = tok
			condition = predicate.TruePredicate()
		return subnode.Subnode(subnode_name.value, condition, nlg)
	
	def continue_conditions_section(self, tok):
		return tok
		
	def assignment(self, tok):
		return assignment.Assignment(tok[0], tok[1])
		
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
		return "entry_conditions_takeover", tok
		
	### SET STATE
	def set_state_section(self, tok):
		return "set_state", assignment.AssignmentList(tok)
		
	### SUBNODE
	def subnodes_section(self, tok):
		return "subnodes", subnode.SubnodeList(tok)
		
	### SET STATE AFTER
	def set_state_after_section(self, tok):
		return "set_state_after", tok
	
	def document(self, tok):
		for x in tok:
			print(x)
		return tok

json_parser = Lark(grammar, start='document', parser='lalr', transformer=SupernodeMaker(), import_paths=[BASE_PATH])
def parse(text):
	return json_parser.parse(text)