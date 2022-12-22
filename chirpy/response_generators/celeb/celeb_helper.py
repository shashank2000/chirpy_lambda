import logging

logger = logging.getLogger('chirpylogger')

CELEBS = ["taylor swift", "ryan reynolds", "nathan fillion", "matthew mcconaughey"]

def is_known_celeb(entity_name):
    logger.primary_info(entity_name.lower() in CELEBS)
    logger.primary_info(entity_name)
    return entity_name.lower() in CELEBS