from chirpy.response_generators.wiki2 import wiki_utils 
from chirpy.core.response_generator import nlg_helper
import logging

logger = logging.getLogger('chirpylogger')

es = wiki_utils.es

@nlg_helper
def get_overview(rg, entity):
    query = {
        "query": {
            "match": {
                "doc_title": entity
            }
        }
    }
    result = es.search(index='enwiki-20201201-sections', body=query, size=1)
    if not result or result['hits']['total']['value'] == 0:
        logger.warning(f"Could not find overview for {entity}. Indicative of mismatch between entity linker and wiki corpus")
        return None
    section = wiki_utils.convert_to_dict(result['hits']['hits'][0])
    summary = wiki_utils.get_summary(section['text'], wiki_utils.get_sentseg_fn(rg), max_words=50, max_sents=2)
    logger.primary_info(f"Summary is: {summary}")
    summary = wiki_utils.clean_wiki_text(summary)
    logger.primary_info(f"Summary after clean is: {summary}")
    if wiki_utils.contains_offensive(summary):
        logger.primary_info(f"Found {entity}'s overview: {summary} to be offensive, discarding it")
        return None
    return summary