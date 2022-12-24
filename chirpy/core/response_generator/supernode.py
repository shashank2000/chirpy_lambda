import os
import yaml

from chirpy.core.callables import NamedCallable
from chirpy.core.state_manager import StateManager
from chirpy.core.regex import response_lists
from chirpy.core.response_generator.response_type import *
from chirpy.core.response_generator.neural_helpers import is_two_part, NEURAL_DECODE_CONFIG, get_random_fallback_neural_response
from chirpy.core.response_generator.state import NO_UPDATE, BaseState, BaseConditionalState
from chirpy.core.response_generator.neural_helpers import get_neural_fallback_handoff, neural_response_filtering
from chirpy.core.response_generator.treelet import Treelet
from chirpy.core.response_generator_datatypes import ResponseGeneratorResult, PromptResult, emptyResult, \
	emptyResult_with_conditional_state, emptyPrompt, UpdateEntity, AnswerType
from chirpy.core.response_generator.helpers import *
from chirpy.core.response_priority import ResponsePriority
from chirpy.core.util import load_text_file, infl, get_none_replace
from typing import Set, Optional, List, Dict
import logging
import os
import random

from importlib import import_module

from concurrent import futures

import inflect
engine = inflect.engine()


logger = logging.getLogger('chirpylogger')


# 		for cases in self.nlg_yamls[supernode]['unconditional_prompt']:
# 	requirements = cases['entry_conditions']
# 	matches_entry_criteria = True
# 	for key in requirements:
# 		if flags[key] != requirements[key]:
# 			matches_entry_criteria = False
# 			break
# 	if matches_entry_criteria:
# 		return cases['case_name'], cases['prompt']
# return None



BASE_PATH = os.path.join(os.path.dirname(__file__), '../../symbolic_rgs')

def lookup_value(value_name, contexts):
	if '.' in value_name:
		assert len(value_name.split('.')) == 2, "Only one namespace allowed."
		namespace_name, value_name = value_name.split('.')
		namespace = contexts[namespace_name]
		return namespace[value_name]
	else:
		assert False, f"Need a namespace for value name {value_name}."

def evaluate_nlg_call(data, python_context, contexts):
	if isinstance(data, list):
		return evaluate_nlg_calls(data, python_context, contexts)
	if isinstance(data, str): # plain text
		return data
	if isinstance(data, int): # number
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
	elif type == 'val':
		assert isinstance(nlg_params, str)
		return lookup_value(nlg_params, contexts)
	elif type == 'nlg_helper':
		assert isinstance(nlg_params, dict)
		function_name = nlg_params['name']
		# logger.warning(f"NLG helpers dir: {dir(python_context['supernode'].nlg_helpers)}")
		assert hasattr(python_context['supernode'].nlg_helpers, function_name), f"Function name {function_name} not found"
		args = nlg_params.get('args', [])
		args = [evaluate_nlg_call(arg, python_context, contexts) for arg in args]
		args = [python_context['rg']] + args  # Add RG as first argument
		return getattr(python_context['supernode'].nlg_helpers, function_name)(*args)
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
	elif type == "neural_generation":
		assert isinstance(nlg_params, dict)
		prefix = evaluate_nlg_calls(nlg_params['prefix'], python_context, contexts)
		return python_context['rg'].get_neural_response(prefix=prefix)
	elif type == "sample_template":
		assert isinstance(nlg_params, str)
		if nlg_params not in global_templates_cache:
				raise KeyError(f'{nlg_params} template not found!')
		return global_templates_cache[nlg_params].sample()
	elif type == 'combine':
		# allows you to chain nlg calls together in order to create one output
		assert isinstance(nlg_params, list)
		return evaluate_nlg_calls(nlg_params, python_context, contexts)
	elif type == 'one of':
		return evaluate_nlg_call(random.choice(nlg_params), python_context, contexts)
	elif type == 'constant':
		return nlg_params
	else:
		assert False, f"Generation type {type} not found!"


		
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
	
def compute_entry_condition(entry_condition, python_context, contexts):
	assert len(entry_condition) == 1
	condition_style, var_data = list(entry_condition.items())[0]
	if condition_style == 'and':
		return all(compute_entry_condition(ent, python_context, contexts) for ent in var_data)
	elif condition_style == 'or':
		return any(compute_entry_condition(ent, python_context, contexts) for ent in var_data)
	elif condition_style == 'disabled':
		return not var_data
	elif condition_style == 'is_one_of':
		var_value = lookup_value(var_data['name'], contexts)
		return CONDITION_STYLE_TO_BEHAVIOR[condition_style](var_value, var_data['values'])
	elif condition_style == 'is_not_one_of':
		var_value = lookup_value(var_data['name'], contexts)
		return CONDITION_STYLE_TO_BEHAVIOR[condition_style](var_value, var_data['values'])
	elif condition_style == 'is_greater_than':
		# is_greater_than (returns true if variable associated with name > value + additional_target)
		#   name: variable to look up
		#   value: an integer value
		#   additional_target: variable to look up (can be omitted). additional_target set to 0 if omitted
		var_value = lookup_value(var_data['name'], contexts)
		additional_target = 0
		if 'additional_target' in var_data:
			additional_target = lookup_value(var_data['additional_target'], contexts)
		return CONDITION_STYLE_TO_BEHAVIOR[condition_style](var_value, var_data['value'] + additional_target)

	if condition_style == 'is_value':
		var_name = var_data['name']
		var_expected_value = evaluate_nlg_call(var_data['value'], python_context, contexts)
	else:
		var_name = var_data
	
	assert condition_style in CONDITION_STYLE_TO_BEHAVIOR, f"Condition style {condition_style} is not recognized!"
	validity_func = CONDITION_STYLE_TO_BEHAVIOR[condition_style]
	
	evaluated_value = lookup_value(var_name, contexts)
	
	if condition_style == 'is_value':
		result = validity_func(evaluated_value, var_expected_value)
	else:	
		result = validity_func(evaluated_value)
		
	return result

def is_valid(entry_conditions, python_context, contexts):
	for entry_condition_dict in entry_conditions:
		if not compute_entry_condition(entry_condition_dict, python_context, contexts):
			return False

	return True

class Prompt:
	def __init__(self, data):
		self.data = data
		self.entry_conditions = get_none_replace(data, 'entry_conditions', [])
		self.prompt_text = data.get('prompt_text')
		self.name = data['prompt_name']
		self.updates = get_none_replace(data, 'set_state', {})

	def is_valid(self, python_context, contexts):
		return is_valid(self.entry_conditions, python_context, contexts)

	def get_prompt_text(self, python_context, contexts):
		return evaluate_nlg_calls(self.prompt_text, python_context, contexts)

	def get_state_updates(self, python_context, contexts):
		return {
			value_name: evaluate_nlg_calls(value_data, python_context, contexts)
			for value_name, value_data in self.updates.items()
		}

	def __str__(self):
		return f'Prompt text: ({self.prompt_text})'

	def __repr__(self):
		return str(self)

class Subnode:
	def __init__(self, data):
		self.data = data
		self.entry_conditions = get_none_replace(data, 'entry_conditions', [])
		self.response = data.get('response')
		self.name = data['node_name']
		self.updates = get_none_replace(data, 'set_state', {})
		
	def is_valid(self, python_context, contexts):
		return is_valid(self.entry_conditions, python_context, contexts)
		
	def get_response(self, python_context, contexts):
		return evaluate_nlg_calls(self.response, python_context, contexts)
		
	def get_state_updates(self, python_context, contexts):
		return {
			value_name: evaluate_nlg_calls(value_data, python_context, contexts)
			for value_name, value_data in self.updates.items()
		}
		
	def __str__(self):
		return f'Subnode({self.name})'

	def __repr__(self):
		return str(self)

from abc import ABC, abstractmethod

class Condition(ABC):
	@abstractmethod
	def get_priority(self):
		pass


class Supernode:
	def __init__(self, name):
		self.yaml_path = os.path.join(BASE_PATH, name)
		with open(os.path.join(self.yaml_path, 'supernode.yaml'), 'r') as f:
			self.content = yaml.safe_load(f)
			
		ALLOWED_KEYS = [
			'entry_conditions',
			'entry_conditions_takeover',
			'continue_conditions',
			'prompts',
			'locals',
			'subnodes',
			'set_state',
			'set_state_after'
		]
		
		invalid_keys = set(self.content.keys()) - set(ALLOWED_KEYS)
		assert len(invalid_keys) == 0, f"Invalid key: {invalid_keys}"
			
		self.entry_conditions = get_none_replace(self.content, 'entry_conditions', [])
		self.entry_conditions_takeover = get_none_replace(self.content, 'entry_conditions_takeover', 'disallow')
		self.continue_conditions = get_none_replace(self.content, 'continue_conditions', [])
		self.locals = self.content['locals']
		self.subnodes = self.load_subnodes(self.content['subnodes'])
		self.updates = get_none_replace(self.content, 'set_state', {})
		self.updates_after = get_none_replace(self.content, 'set_state_after', {})
		self.prompts = self.load_prompts(self.content['prompts'])
		self.name = name
		
		self.nlu = import_module(f'chirpy.symbolic_rgs.{name}.nlu')
		self.nlg_helpers = import_module(f'chirpy.symbolic_rgs.{name}.nlg_helpers')		
		
	def is_eligible(self, python_context, contexts):
		return is_valid(self.requirements, python_context, contexts)

	def get_global_subnodes(self):
		return []
		
	def load_subnodes(self, subnode_data):
		return [Subnode(data) for data in subnode_data]

	def get_optimal_subnode(self, python_context, contexts):
		possible_subnodes = [subnode for subnode in self.subnodes + self.get_global_subnodes() if subnode.is_valid(python_context, contexts)]
		assert len(possible_subnodes), "No subnode found!"
		
		# for now, just return the first possible subnode
		return possible_subnodes[0]
		
	def load_prompts(self, prompt_data):
		return [Prompt(data) for data in prompt_data]

	def get_optimal_prompt(self, python_context, contexts):
		possible_prompts = [prompt.get_prompt_text(python_context, contexts) for prompt in self.prompts if
							 prompt.is_valid(python_context, contexts)]
		assert len(possible_prompts), "No prompt found!"

		# for now, just return the first possible subnode
		return possible_prompts[0]

	def evaluate_locals(self, python_context, contexts):
		output = {}
		contexts['locals'] = output
		for local_key, local_values in self.locals.items():
			output[local_key] = evaluate_nlg_calls(local_values, python_context, contexts)
		return output
	
	def can_start(self, python_context, contexts, return_specificity=False):
		result = is_valid(self.entry_conditions, python_context, contexts)
		if return_specificity:
			return (len(self.entry_flag_conditions), len(self.entry_state_conditions) + 1) if result else (0, 0)
		else:
			return result

	def compute_priority(self, entry_conditions):
		"""TODO: In the future, we would like to dynamically learn this (perhaps via RL)."""



	def can_takeover(self, python_context, contexts, return_specificity=False):
		if self.entry_conditions_takeover == 'disallow':
			# Supernode with no entry conditions cannot takeover
			return False

		result = is_valid(self.entry_conditions_takeover, python_context, contexts)
		logger.info(f"Can_takeover for {self.name} logged {result}")
		if return_specificity:
			return len(self.entry_conditions_takeover) if result else 0
		else:
			return result
		
	def can_continue(self, python_context, contexts):
		result = is_valid(self.continue_conditions, python_context, contexts)
		return result
		
	def get_flags(self, rg, state, utterance):
		flags = self.nlu.get_flags(rg, state, utterance)
		return flags

	def get_background_flags(self, rg, utterance):
		# background_flags: flags to update even if this supernode was not chosen
		flags = self.nlu.get_background_flags(rg, utterance)
		return flags

	def get_state_updates(self, python_context, contexts):
		return {
			value_name: evaluate_nlg_calls_or_constant(value_data, python_context, contexts)
			for value_name, value_data in self.updates.items()
		}

	def get_state_updates_after(self, python_context, contexts):
		return {
			value_name: evaluate_nlg_calls_or_constant(value_data, python_context, contexts)
			for value_name, value_data in self.updates_after.items()
		}
			
		
	def __str__(self):
		return f"Supernode({self.yaml_path})"
		
	def __repr__(self):
		return str(self)