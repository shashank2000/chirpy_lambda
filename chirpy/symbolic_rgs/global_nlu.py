from chirpy.core.response_generator.nlu import *

@nlu_processing
def get_flags(context):
	utterance = context.utterance
	if 'what' in utterance:
		ADD_NLU_FLAG("GlobalFlag__WHAT")
	if 'why' in utterance:
		ADD_NLU_FLAG("GlobalFlag__WHY")