from chirpy.core.response_generator.nlu import nlu_processing
import os 
from os.path import abspath, dirname
import json 

# we can actually just get rid of this file I/O and just put the list of animals here
with open(os.path.join(abspath(dirname(__file__)), 'animals.json')) as datafile:
    f = json.load(datafile)
    ANIMALS = f['animals']

# leaving helper function here instead of making new directory in response_generators
def is_known_animal(entity):
    if entity in ANIMALS:
        return True
    return False


@nlu_processing
def get_flags(context):
    entity = context.utilities["cur_entity"]
    if entity is None: return
    
    entity_name = entity.name.lower()
    if is_known_animal(entity_name):
        if entity_name == 'dog':
            ADD_NLU_FLAG('PETS__user_has_dog')
        if entity_name == 'rabbit':
            ADD_NLU_FLAG('PETS__user_has_rabbit')
        if entity_name == 'cat':
            ADD_NLU_FLAG('PETS__user_has_cat')