from chirpy.core.response_generator import nlg_helper

@nlg_helper
def get_adjective_form(genre_str):
    return genre_str[:-6] if genre_str.endswith('music') else genre_str

@nlg_helper
def get_plural_form(work_descriptor):
    return work_descriptor + 's'