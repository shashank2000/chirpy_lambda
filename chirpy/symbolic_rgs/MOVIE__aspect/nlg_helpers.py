from chirpy.response_generators.movie import movie_helpers
from chirpy.core.response_generator import nlg_helper
from chirpy.response_generators.movie.expression_lists import YES, NO
from chirpy.core.camel.context import Context


import logging
import re

logger = logging.getLogger('chirpylogger')


def get_regex_match_category(response):
    regex_expressions = {
        'acting': re.compile(r'\bact\b|\bacts\b|\bacted\b|\bacting\b|\bactor\b|\bactress\b|\bactors\b|\bactresses\b', re.I),
        'directing': re.compile(r'\bdirector\b|\bdirectors\b|\bdirecting\b', re.I),
        'message': re.compile(r'\bmessage\b|\bmessage\b|\btheme\b|\bmoral\b|\bsignificance\b', re.I),
        'plot': re.compile(r'\bplot\b|story\sline\b|\bscene\b', re.I)
    }
    reasons = []
    for category, regex in regex_expressions.items():
        if regex.findall(response):
            reasons.append(category)
    return reasons


@nlg_helper
def get_user_reasons(response):
    reasons = get_regex_match_category(response)
    logger.warning(f'reasons are {reasons}')
    if reasons:
        return reasons[0]
    else:
        return None


    # return sentence
    # import openai
    # openai.api_key = "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"

    # def generate(prompt, **kwargs):
    #     completion = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=256, temperature=0.7, **kwargs)
    #     return completion.choices[0]
    
    # output = generate(
    #     f"""
    #     List the reasons why the user liked the movie and return it as an object. For instance,
    #     if the commentary is 'I liked the movie since I like the director and the actors',
    #     then the correct analysis would include 'director' and 'actors'.

    #     User commentary: {sentence}
    #     """
    # )['text']

    # all_keys = ast.literal_eval(output)
    # return list(all_keys.keys())