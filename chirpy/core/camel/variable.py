from dataclasses import dataclass


@dataclass
class Variable:
	namespace : str
	name : str
	def generate(self, python_context, contexts):
		return contexts[self.namespace][self.name]