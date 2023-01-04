from chirpy.core.response_generator.nlu import *

@nlu_processing
def get_flags(context):
	utterance = context.utterance
	current_state = context.state_manager.current_state
	if 'what' in utterance:
		ADD_NLU_FLAG("GlobalFlag__WHAT")
	if 'why' in utterance:
		ADD_NLU_FLAG("GlobalFlag__WHY")
	if current_state.entity_tracker.cur_entity and current_state.navigational_intent.pos_intent:
		ADD_NLU_FLAG("GlobalFlag__SpecifiedEntity", current_state.entity_tracker.cur_entity)