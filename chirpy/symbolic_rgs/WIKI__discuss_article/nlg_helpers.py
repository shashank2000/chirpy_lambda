from chirpy.response_generators.wiki2 import wiki_utils 
from chirpy.core.response_generator import nlg_helper
import logging

logger = logging.getLogger('chirpylogger')

es = wiki_utils.es

@nlg_helper
def discuss_article(rg, entity):
    results = es.search(index='enwiki-20201201-sections', body={
        "query": {
            "match": {
                "doc_title": entity.name
            }
        }
    })
    sections = results['hits']['hits']
    sections = [(section['_source']['title'], section['_source']['text']) for section in sections]
    print("sdlkajsldkjaslksections", sections)
    sentences = wiki_utils.get_sentences_from_sections_tfidf(sections, rg.state_manager, first_turn=rg.active_last_turn())
    print("sdlkajsldkjaslksentences", sentences)
    return "done"