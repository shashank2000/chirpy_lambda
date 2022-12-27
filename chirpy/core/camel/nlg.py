from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List, Any, Optional

from chirpy.core.camel.variable import Variable

import os

BASE_PATH = os.path.join(os.path.dirname(__file__), '../../symbolic_rgs')


def lookup_value(value_name, contexts):
    if '.' in value_name:
        assert len(value_name.split('.')) == 2, "Only one namespace allowed."
        namespace_name, value_name = value_name.split('.')
        namespace = contexts[namespace_name]
        return namespace[value_name]
    else:
        assert False, f"Need a namespace for value name {value_name}."


PUNCTUATION = ['.', ',', '?', '!', ':', ';']


def spacingaware_join(x):
    result = ""
    for idx, item in enumerate(x):
        assert isinstance(item, str), f"Item {item} (from {x}) is not a string"
        if idx != 0 and not any(item.startswith(punct) for punct in PUNCTUATION):
            result += " "
        result += item
    return result


def evaluate_nlg_calls(datas, python_context, contexts):
    output = []
    if isinstance(datas, str) or isinstance(datas, dict):
        return evaluate_nlg_call(datas, python_context, contexts)
    if len(datas) == 1:
        return evaluate_nlg_call(datas[0], python_context, contexts)
    for elem in datas:
        out = evaluate_nlg_call(elem, python_context, contexts)
        if not isinstance(out, str):
            logger.error(f"{out} is not a string. This is not ok unless you are debugging.")
            out = str(out)
        output.append(out)

    return spacingaware_join(output)


def evaluate_nlg_calls_or_constant(datas, python_context, contexts):
    if isinstance(datas, dict):
        assert len(datas) == 1, "should be a dict with key constant"
        return datas['constant']
    return evaluate_nlg_calls(datas, python_context, contexts)


CONDITION_STYLE_TO_BEHAVIOR = {
    'is_none': (lambda val: (val is None)),
    'is_not_none': (lambda val: (val is not None)),
    'is_true': (lambda val: (val is True)),
    'is_false': (lambda val: (val is False)),
    'is_value': (lambda val, target: (val == target)),
    'is_one_of': (lambda val, target: (val in target)),
    'is_not_one_of': (lambda val, target: (val not in target)),
    'is_greater_than': (lambda val, target: (val > target)),
}



def is_valid(entry_conditions, python_context, contexts):
    for entry_condition_dict in entry_conditions:
        if not compute_entry_condition(entry_condition_dict, python_context, contexts):
            return False

    return True

def evaluate_nlg_call(data, python_context, contexts):
    if isinstance(data, list):
        return evaluate_nlg_calls(data, python_context, contexts)
    if isinstance(data, str):  # plain text
        return data
    if isinstance(data, int):  # number
        return data

    assert isinstance(data, dict) and len(data) == 1, f"Failure: data is {data}"
    type = next(iter(data))
    nlg_params = data[type]
    if type == 'eval':
        assert isinstance(nlg_params, str)
        return effify(nlg_params, global_context=python_context)
    elif type == 'bool':
        assert isinstance(nlg_params, list)
        return is_valid(nlg_params, python_context, contexts)
    
    elif type == 'inflect':
        assert isinstance(nlg_params, dict)
        inflect_token = nlg_params['inflect_token']
        inflect_val = lookup_value(nlg_params['inflect_entity'], contexts)
        return infl(inflect_token, inflect_val.is_plural)
    elif type == 'inflect_engine':
        assert isinstance(nlg_params, dict)
        inflect_function = nlg_params['type']
        inflect_input = evaluate_nlg_call(nlg_params['str'], python_context, contexts)
        return getattr(engine, inflect_function)(inflect_input)
    elif type == "sample_template":
        assert isinstance(nlg_params, str)
        if nlg_params not in global_templates_cache:
            raise KeyError(f'{nlg_params} template not found!')
        return global_templates_cache[nlg_params].sample()
   
    elif type == 'one of':
        return evaluate_nlg_call(random.choice(nlg_params), python_context, contexts)
    elif type == 'constant':
        return nlg_params
    else:
        assert False, f"Generation type {type} not found!"
        
class NLGNode(ABC):
    @abstractmethod
    def generate(self, python_context, contexts):
        pass


@dataclass
class NeuralGeneration(NLGNode):
    prefix : NLGNode
    def generate(self, python_context, contexts):
        return python_context['rg'].get_neural_response(prefix=self.prefix.generate())

    
@dataclass
class Val:
    variable : Variable
    def generate(self, *args):
        return self.variable.generate(*args)
        
@dataclass
class NLGHelper:
    name : str
    args : List[NLGNode]
    def generate(self, python_context, contexts):
        assert hasattr(python_context['supernode'].nlg_helpers, self.name), f"Function not found: {function_name} (available: {dir(python_context['supernode'].nlg_helpers).filter(lambda x: not x.startswith('_'))})"
        args = [evaluate_nlg_call(arg, python_context, contexts) for arg in self.args]
        return getattr(python_context['supernode'].nlg_helpers, function_name)(*args)

@dataclass
class Inflect:
    inflect_token : NLGNode
    inflect_entity : Variable
    def generate(self, python_context, contexts):
        input = self.inflect_token.generate(python_context, contexts)
        val = self.inflect_entity.generate(python_context, contexts)
        assert isinstance(val, WikiEntity)
        return infl(input, val)

@dataclass
class InflectEngine(NLGNode):
    type : str
    string : NLGNode
    def generate(self, *args):
        input = self.string.generate(*args)
        return getattr(engine, self.type)(input)

@dataclass
class OneOf(NLGNode):
    options : List[NLGNode]
    def generate(self, python_context, contexts):
        return random.choice(options).generate(python_context, contexts)
        
@dataclass
class Constant(NLGNode):
    val : Any
    def generate(self, python_context, contexts):
        return val
        

@dataclass
class NLGList(NLGNode):
    items : List[NLGNode]
    def generate(self, python_context, contexts):
        return spacingaware_join([x.generate(python_context, contexts) for x in items])