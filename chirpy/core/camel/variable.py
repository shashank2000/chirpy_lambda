from dataclasses import dataclass


@dataclass
class Variable:
	namespace : str
	name : str
	def generate(self, context):
		assert hasattr(context, self.namespace.lower()), f"Namespace {self.namespace} not found!"
		namespace = getattr(context, self.namespace.lower())
		return getattr(context, self.namespace.lower())[self.name]