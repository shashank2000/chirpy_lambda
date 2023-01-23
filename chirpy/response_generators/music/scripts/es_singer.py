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


def gen_list_of_terms():
    times = ['20th', '21st']
    nations = ['American', 'British', 'English', 'Indian', 'Japanese', 'French', 'Spanish', 'Italian', 'Australian',
               'German', 'Mexican', 'Swedish', 'Danish', 'South Korean']
    professions = ['singers', 'rappers', 'musicians']
    template = "{tms}-century {nation} {prof}"
    all_temps = []
    for t in times:
        for n in nations:
            for p in professions:
                all_temps.append(template.format(tms=t, nation=n, prof=p))
    for n in nations:
        for p in professions:
            all_temps.append(n + " " + p)

    all_temps.extend(['K-pop singers', 'J-pop singers', 'K-pop music groups'])
    return all_temps

def scrape_es():
    es = get_elasticsearch()
    # https://en.wikipedia.org/wiki/Category:Singing
    all_temps_categories = gen_list_of_terms()
    all_temps_wiki_categories = ['singer', 'vocalist', 'musician', 'musical group']
    all_singers = set()
    for t in all_temps_categories:
        query = {'query': {'bool': {"must": [{'terms': {'categories.keyword': [t]}},
                                             {"range": {"pageview": {"gte": 3000}}}]}},
                 'sort': {'pageview': 'desc'}}
        results = query_es_index(es, ARTICLES_INDEX_NAME, query, size=MAX_ES_SEARCH_SIZE,
                                 timeout=ANCHORTEXT_QUERY_TIMEOUT,
                                 filter_path=['hits.hits._source.{}'.format(field) for field in FIELDS_FILTER])
        for s in results:
            all_singers.add(s['_source']['doc_title'])

    for t in all_temps_wiki_categories:
        query = {'query': {'bool': {"must": [{'terms': {'wikidata_categories_all.keyword': [t]}}]}},
                'sort': {'pageview': 'desc'}}
        results = query_es_index(es, ARTICLES_INDEX_NAME, query, size=MAX_ES_SEARCH_SIZE,
                                 timeout=ANCHORTEXT_QUERY_TIMEOUT,
                                 filter_path=['hits.hits._source.{}'.format(field) for field in FIELDS_FILTER])
        for s in results:
            all_singers.add(s['_source']['doc_title'])

    print(len(all_singers))    # 3236 entities
    return all_singers

if __name__ == "__main__":
    all_singers = list(scrape_es())
    pickle.dump(all_singers, open("scraped_singers.p", "wb+"))
