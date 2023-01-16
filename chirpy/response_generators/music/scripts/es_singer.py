import json
import logging
import pickle

from chirpy.core.util import query_es_index, get_elasticsearch
import tqdm

from chirpy.core.logging_utils import setup_logger, PROD_LOGGER_SETTINGS

setup_logger(PROD_LOGGER_SETTINGS)

MAX_ES_SEARCH_SIZE = 500

ANCHORTEXT_QUERY_TIMEOUT = 300.0  # seconds
ENTITYNAME_QUERY_TIMEOUT = 100.0  # seconds

ARTICLES_INDEX_NAME = 'enwiki-20201201-articles'

# These are the fields we DO want to fetch from ES
FIELDS_FILTER = ['doc_title', 'doc_id', 'categories', 'pageview', 'linkable_span_info', 'wikidata_categories_all',
                 'redirects', 'plural']


logger = logging.getLogger('chirpylogger')


def scrape_es():
    es = get_elasticsearch()
    all_temps = ['string instrument']
    all_musical_instruments = []
    for t in all_temps:
        query = {'query': {'bool': {"must": [{'terms': {'wikidata_categories_all.keyword': [t]}}]}},
                 'sort': {'pageview': 'desc'}}
        results = query_es_index(es, ARTICLES_INDEX_NAME, query, size=MAX_ES_SEARCH_SIZE,
                                 timeout=ANCHORTEXT_QUERY_TIMEOUT,
                                 filter_path=['hits.hits._source.{}'.format(field) for field in FIELDS_FILTER])
        for s in results:
            all_musical_instruments.append(s['_source']['doc_title'])

    return all_musical_instruments

if __name__ == "__main__":
    all_musical_instruments = scrape_es()
    pickle.dump(all_musical_instruments, open("scraped_musical_instruments.p", "wb+"))
