from chirpy.core.entity_linker.entity_groups import EntityGroupsForExpectedType

def set_pet_type(cur_entity):
    if not cur_entity:
        return None
    if EntityGroupsForExpectedType.pet.matches(cur_entity):
        return cur_entity.name.lower()
    return None
