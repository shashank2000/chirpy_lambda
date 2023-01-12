from dataclasses import dataclass
from typing import Dict
from chirpy.core.response_generator.response_type import get_intent_flags
from chirpy.core.response_generator.nlu import get_default_flags
from chirpy.symbolic_rgs import global_nlu
from chirpy.core.regex.templates import *

import json

logger = logging.getLogger('chirpylogger')


def get_current_entity(state_manager):
	current_state = state_manager.current_state
	return current_state.entity_tracker.cur_entity

def get_utilities(state_manager, supernode):
	current_entity = get_current_entity(state_manager)
	if state_manager.last_state_response:
		last_utterance = state_manager.last_state_response
	else:
		last_utterance = ""
	return {
		"last_utterance": last_utterance,
		"cur_entity": current_entity,
		"cur_supernode": supernode.name if supernode else "",
		"cur_turn_num": state_manager.current_state.turn_num,
		"response_text" : "",
	}


def get_global_flags(context):
	# response types
	global_flags = get_intent_flags(context.state_manager, context.utterance)
	
	# map from string to None / template
	abrupt_initiative_templates = {
		"weather": WeatherTemplate(),   # problems
		"repeat": SayThatAgainTemplate(),
		# "correct_name":
		"request_name": RequestNameTemplate(),
		# "age"
		# "clarification"
		# "abilities"
		# "personal"
		# "interrupt"
		"chatty": ChattyTemplate(),
		# "story"
		# "personal_problem"
		# "anything"
	}
	
	global_flags.update({f"GlobalFlag__Initiative__{k}": bool(v.execute(context.utterance)) for k, v in abrupt_initiative_templates.items()})
	global_flags.update(global_nlu.get_flags(context))
			
	return global_flags

@dataclass
class Context:
	supernode : "Supernode"
	flags : Dict
	state : Dict
	utilities : Dict
	locals : Dict
	utterance : str
	state_manager : "StateManager"

	@classmethod
	def get_context(cls, state, state_manager, supernode=None):
		flags = get_default_flags()
		self = cls(
			supernode=supernode,
			state=state,
			flags=flags,
			utilities=get_utilities(state_manager, supernode),
			locals=state.entry_locals,
			utterance=state.utterance,
			state_manager=state_manager
		)
		self.flags.update(get_global_flags(self))
		if supernode is not None:
			self.flags.update(supernode.get_flags(self))
			logger.primary_info(f"Non-null flags for supernode {supernode} are: {[x for x in flags if bool(flags[x])]}")
		return self
		
	@property
	def supernodeturns(self):
		return self.state.turns_history

	def update_with_background_flags(self, supernodes):
			"""Update context's flags with all background flags from all supernodes."""
			_flags = {}
			for supernode in supernodes:
					bg_flags = supernode.get_background_flags(self)
					_flags.update(bg_flags)
			self.flags.update(_flags)

	def set(self, variable, value):
		namespace = getattr(self, variable.namespace.lower())
		namespace[variable.name] = value

	def setDictionary(self, variable, keys, value):
		if len(keys) == 0:
			return self.set(variable, value)
		namespace = getattr(self, variable.namespace.lower())
		dictionary = namespace[variable.name]
		for key in keys[:-1]:
			dictionary = dictionary[key.generate(self)]
		dictionary[keys[-1].generate(self)] = value

	def compute_entry_locals(self):
		self.supernode.entry_locals.evaluate(self)
		logger.debug(f"Finished evaluating entry locals: {'; '.join((k + ': ' + str(v)) for (k, v) in self.locals.items())}")

	def compute_locals(self):
		self.supernode.locals.evaluate(self)
		logger.debug(f"Finished evaluating locals: {'; '.join((k + ': ' + str(v)) for (k, v) in self.locals.items())}")
		
	def log_state(self):
		logger.bluejay(f"rg_state: {json.dumps(self.state.to_serializable())}")
		