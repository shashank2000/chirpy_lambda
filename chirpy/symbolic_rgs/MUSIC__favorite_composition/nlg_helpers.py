from chirpy.core.response_generator import nlg_helper

@nlg_helper
def get_possessive_form(composer_name):
    return composer_name + "'s" if not composer_name.endswith('s') else composer_name + "'"