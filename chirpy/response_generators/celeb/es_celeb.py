import pickle

from chirpy.core.util import query_es_index, get_elasticsearch

MAX_ES_SEARCH_SIZE = 500

ANCHORTEXT_QUERY_TIMEOUT = 3.0  # seconds
ENTITYNAME_QUERY_TIMEOUT = 1.0  # seconds

ARTICLES_INDEX_NAME = 'enwiki-20201201-articles'

# These are the fields we DO want to fetch from ES
FIELDS_FILTER = ['doc_title', 'doc_id', 'categories', 'pageview', 'linkable_span_info', 'wikidata_categories_all',
                 'redirects', 'plural']


def gen_list_of_terms():
    times = ['20th', '21st']
    nations = ['American', 'British', 'English', 'Indian', 'Japanese', 'French', 'Spanish', 'Italian', 'Australian',
               'German', 'Mexican', 'Swedish', 'Danish']
    professions = ['male actors', 'female actors', 'actresses', 'singers', 'rappers', 'YouTubers', 'bloggers']
    template = "{tms}-century {nation} {prof}"
    all_temps = []
    for t in times:
        for n in nations:
            for p in professions:
                all_temps.append(template.format(tms=t, nation=n, prof=p))
    return all_temps


def scrape_es():
    all_temps = gen_list_of_terms()
    all_celebs = []
    for t in all_temps:
        query = {'query': {'bool': {"must": [{'terms': {'categories.keyword': [t]}},
                                             {"range": {"pageview": {"gte": 20000}}}]}},
                 'sort': {'pageview': 'desc'}}
        results = query_es_index(es, ARTICLES_INDEX_NAME, query, size=MAX_ES_SEARCH_SIZE,
                                 timeout=ANCHORTEXT_QUERY_TIMEOUT,
                                 filter_path=['hits.hits._source.{}'.format(field) for field in FIELDS_FILTER])
        for s in results:
            all_celebs.append(s['_source']['doc_title'])
    all_celebs = list(set(all_celebs))
    print(len(all_celebs))
    return all_celebs

if __name__ == "__main__":
    es = get_elasticsearch()
    ent = "Castle (TV series)"

    query = {'query': {'bool': {"must": [{'terms': {'categories.keyword': ["20th-century American male actors"]}},
                                         {"range": {"pageview": {"gte": 100000}}}]}},
             'sort': {'pageview': 'desc'}}
    query_term = {'query': {'bool': {'should': [
        {'terms': {'doc_title.keyword': [ent]}}]}},
        'sort': {'pageview': 'desc'}}
    results = query_es_index(es, ARTICLES_INDEX_NAME, query_term, size=MAX_ES_SEARCH_SIZE,
                             timeout=ANCHORTEXT_QUERY_TIMEOUT,
                             filter_path=['hits.hits._source.{}'.format(field) for field in FIELDS_FILTER])
    for r in results:
        print(r['_source'].keys())
    print(results)

    # all_celebs = scrape_es()
    # pickle.dump(all_celebs, open("scraped_celebs.p", "wb+"))
