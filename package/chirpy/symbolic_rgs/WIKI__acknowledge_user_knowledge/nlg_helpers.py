from chirpy.core.entity_linker.entity_linker import WikiEntity
from chirpy.core.response_generator import nlg_helper
import random
import logging

logger = logging.getLogger('chirpylogger')

@nlg_helper
def get_opinion(entity: WikiEntity, isNeutral: bool, isPositive: bool) -> str:
    # topic = entity.talkable_name.lower()
    # pos_reasons, neg_reasons = get_reasons(topic)
    # logger.primary_info(f"Wiki pos reasons identified: {pos_reasons}")
    # logger.primary_info(f"Wiki neg reasons identified: {neg_reasons}")

    # if isNeutral or isPositive:
    #     reasons = pos_reasons
    #     liking = "like"
    # else:
    #     reasons = neg_reasons
    #     liking = "dislike"
    # if len(reasons) == 0:
    #     logger.primary_info("No reasons found to form opinion")
    #     return ""
    # first_person_reasons = [r for r in reasons if wiki_helpers.contains_first_person_word(r)]
    # non_first_person_reasons = [r for r in reasons if not wiki_helpers.contains_first_person_word(r)]
    # if len(non_first_person_reasons) > 0:
    #     return f"I know some people {liking} it because {random.choice(non_first_person_reasons)}."
    # else:
    #     return f"Personally, I feel like {random.choice(first_person_reasons)}."
    return ""