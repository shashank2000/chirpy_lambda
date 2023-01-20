from chirpy.core.entity_linker.entity_linker import WikiEntity
from chirpy.core.response_generator import nlg_helper

@nlg_helper
def inflect_some_one_thing(entity: WikiEntity):
    # TODO: determine if entity is a person or a thing based on wikidata categories
    return "something"