
class BaseCondition(Condition):
	def __init__(self, predicate, value):

	def __bool__(self):
		return self.evaluate()
	def evaluate(self):
		# TODO
		...

class OperatorCondition(Condition):
	def __init__(self, operator : Callable[[Condition, Condition], Condition] left, right):
		self.left = left
		self.right = right
		self.operator = operator
	def evaluate(self):
		return self.operator(self.left, self.right)

class AndCondition(OperatorCondition):
	def __init__(self, left, right):
		super().__init__(operator=lambda a, b: (a and b), left, right)

class OrCondition(OperatorCondition):
	def __init__(self, left, right):
		super().__init__(operator=lambda a, b: (a or b), left, right)
