from chirpy.core.response_generator import nlg_helper
import logging
import re

logger = logging.getLogger("chirpylogger")


def get_regex_match_category(response):
    regex_expressions = {
        "acting": re.compile(r"\bact\b|\bacts\b|\bacted\b|\bacting\b|\bactor\b|\bactress\b|\bactors\b|\bactresses\b", re.I),
        "directing": re.compile(r"\bdirector\b|\bdirectors\b|\bdirecting\b", re.I),
        "message": re.compile(r"\bmessage\b|\bmessages\b|\btheme\b|\bmoral\b|\bsignificance\b", re.I),
        "plot": re.compile(r"\bplot\b|story\sline\b|\bscene\b", re.I),
    }
    reasons = []
    for category, regex in regex_expressions.items():
        if regex.findall(response):
            reasons.append(category)
    return reasons


@nlg_helper
def get_user_reasons(response):
    reasons = get_regex_match_category(response)
    if reasons:
        return reasons[0]
    else:
        return None