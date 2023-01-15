from chirpy.core.response_generator.nlu import nlu_processing

@nlu_processing
def get_flags(context):
    opinion_yes_words = ["i do", "i sure do"]
    ADD_NLU_FLAG("OPINION__YES", (context.flags['GlobalFlag__YES'] or any(w in context.utterance for w in opinion_yes_words)))
