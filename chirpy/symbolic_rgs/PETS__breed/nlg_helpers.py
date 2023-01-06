import logging
import random
import openai

logger = logging.getLogger('chirpylogger')

openai.api_key = "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"

def generate(prompt, **kwargs):
    # we know input is a breed
    prompt += " is a breed of dogs. "
    completion = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=256, temperature=0.7,
                                          **kwargs)
    return completion.choices[0]

