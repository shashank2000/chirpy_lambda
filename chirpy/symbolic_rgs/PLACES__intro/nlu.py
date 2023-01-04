import pickle as pkl
from chirpy.core.response_generator.nlu import nlu_processing

CITY_INFO_PATH = "/Users/virginiaadams/chirpycardinal/chirpy/symbolic_rgs/PLACES__intro/city_info.pkl"
city_info = pkl.load(open(CITY_INFO_PATH, "rb"))

@nlu_processing
def get_flags(context):
    entity = context.utilities["cur_entity"]
    if entity is None: return
    
    entity_name = entity.name.lower()
    is_known_city = entity_name in city_info
    if is_known_city:
        ADD_NLU_FLAG('PLACES__user_mentioned_city') 
        
@nlu_processing
def get_background_flags(context):
    return