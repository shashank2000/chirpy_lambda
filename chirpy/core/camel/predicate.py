from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
import json

from chirpy.core.camel.variable import Variable
from chirpy.core.camel.nlg import NLGNode
from chirpy.databases.databases import exists
import logging

logger = logging.getLogger("chirpylogger")


@dataclass
class Predicate(ABC):
    @abstractmethod
    def evaluate(self, context, label=""):
        pass


funcs = {
    "IS_NONE": lambda x: x is None,
    "IS_TRUE": lambda x: bool(x),
    "IS_FALSE": lambda x: not bool(x),
}


def get_func(verb):
    return funcs[verb]


def get_score(variable):
    if variable.namespace == "Flags":
        return 100
    elif variable.namespace == "State":
        return 1
    return 1


@dataclass
class VariablePredicate(Predicate):
    verb: str
    variable: Variable

    def evaluate(self, context, label=""):
        val = self.variable.generate(context)
        result = get_func(self.verb)(val)
        log = {
            "val": str(val),
            "variable_name": str(self.variable),
            "verb": self.verb,
            "result": result,
        }
        if label:
            logger.bluejay(f"predicate_{label}//{self.variable}: {json.dumps(log)}")
        return result

    def get_score(self):
        return get_score(self.variable)


@dataclass
class AndPredicate(Predicate):
    pred1: Predicate
    pred2: Predicate

    def evaluate(self, context, label=""):
        return self.pred1.evaluate(context, label) and self.pred2.evaluate(context, label)

    def get_score(self):
        return max(self.pred1.get_score(), self.pred2.get_score())


@dataclass
class OrPredicate(Predicate):
    pred1: Predicate
    pred2: Predicate

    def evaluate(self, context, label=""):
        return self.pred1.evaluate(context, label) or self.pred2.evaluate(context, label)

    def get_score(self):
        return max(self.pred1.get_score(), self.pred2.get_score())


@dataclass
class FalsePredicate(Predicate):
    def evaluate(self, context, label=""):
        return False

    def get_score(self):
        return 0


@dataclass
class TruePredicate(Predicate):
    def evaluate(self, context, label=""):
        return True

    def get_score(self):
        return 0


@dataclass
class VariableIsPredicate(Predicate):
    variable: Variable
    val: NLGNode

    def evaluate(self, context, label=""):
        return self.variable.generate(context) == self.val.generate(context)

    def get_score(self):
        return get_score(self.variable)


@dataclass
class VariableGTPredicate(Predicate):
    variable: Variable
    val: NLGNode

    def evaluate(self, context, label=""):
        return self.variable.generate(context) > self.val.generate(context)

    def get_score(self):
        return get_score(self.variable)


@dataclass
class VariableLTPredicate(Predicate):
    variable: Variable
    val: NLGNode

    def evaluate(self, context, label=""):
        return self.variable.generate(context) < self.val.generate(context)

    def get_score(self):
        return get_score(self.variable)


@dataclass
class VariableInPredicate(Predicate):
    variable: Variable
    vals: List[NLGNode]

    def evaluate(self, context, label=""):
        var = self.variable.generate(context)
        for val in self.vals:
            if var == val.generate(context):
                return True
        return False

    def get_score(self):
        return get_score(self.variable)


@dataclass
class NotPredicate(Predicate):
    predicate: Predicate

    def evaluate(self, context, label=""):
        base = self.predicate.evaluate(context, label)
        return not base

    def get_score(self):
        return self.predicate.get_score()


@dataclass
class ExistsPredicate(Predicate):
    database_name: str
    database_key: List[NLGNode]

    def evaluate(self, context, label=""):
        database_name = self.database_name.generate(context)
        keys = [key.generate(context) for key in self.database_key]
        result = exists(database_name, *keys)
        if label:
            log = {
                "val": result,
                "variable_name": database_name + ", " + ", ".join(keys),
                "verb": "EXISTS",
                "result": result,
            }
            logger.bluejay(f"predicate_{label}//{self.database_name}: {json.dumps(log)}")
        return result

    def get_score(self):
        return 1.0
