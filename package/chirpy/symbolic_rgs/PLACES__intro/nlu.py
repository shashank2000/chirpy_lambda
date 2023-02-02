import pickle as pkl
from chirpy.core.response_generator.nlu import nlu_processing
from chirpy.core.entity_linker.entity_groups import EntityGroupsForExpectedType
import os

CITY_INFO_PATH = "./chirpy/symbolic_rgs/PLACES__intro/city_info.pkl"
city_info = pkl.load(open(CITY_INFO_PATH, "rb"))

@nlu_processing
def get_flags(context):
    entity = context.utilities["cur_entity"]
    if entity is None: return
    if EntityGroupsForExpectedType.location_related.matches(entity):
        ADD_NLU_FLAG('PLACES__user_mentioned_city') 
        
@nlu_processing
def get_background_flags(context):
    return