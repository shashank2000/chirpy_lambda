import logging
import random
from chirpy.core.response_generator import nlg_helper
import openai

logger = logging.getLogger('chirpylogger')

openai.api_key = "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"

@nlg_helper
def generate(prompt, **kwargs):
    breakpoint()
    completion = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=256, temperature=0.7,
                                          **kwargs)
    return completion.choices[0]['text']

