import json
import logging
import pickle

from chirpy.core.util import query_es_index, get_elasticsearch
import tqdm

from chirpy.core.logging_utils import setup_logger, PROD_LOGGER_SETTINGS

setup_logger(PROD_LOGGER_SETTINGS)

MAX_ES_SEARCH_SIZE = 500

ANCHORTEXT_QUERY_TIMEOUT = 3.0  # seconds
ENTITYNAME_QUERY_TIMEOUT = 1.0  # seconds

ARTICLES_INDEX_NAME = 'enwiki-20201201-articles'

# These are the fields we DO want to fetch from ES
FIELDS_FILTER = ['doc_title', 'doc_id', 'categories', 'pageview', 'linkable_span_info', 'wikidata_categories_all',
                 'redirects', 'plural']


logger = logging.getLogger('chirpylogger')

def gen_list_of_terms():
    times = ['20th', '21st']
    nations = ['American', 'British', 'English', 'Indian', 'Japanese', 'French', 'Spanish', 'Italian', 'Australian',
               'German', 'Mexican', 'Swedish', 'Danish']
    professions = ['male actors', 'female actors', 'actresses', 'singers', 'rappers', 'YouTubers', 'bloggers', 'male models', 'female models', 'socialites', 'comedians']
    template = "{tms}-century {nation} {prof}"
    all_temps = []
    for t in times:
        for n in nations:
            for p in professions:
                all_temps.append(template.format(tms=t, nation=n, prof=p))
    for n in nations:
        for p in professions:
            all_temps.append(n + " " + p)
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
            all_celebs.append((s['_source']['doc_title'], s['_source']['pageview'], t))
    print(len(all_celebs))
    # get top 300 for each category
    tops_celebs = {}
    for t in all_temps:
        core_profession = t.split(" ")[-1]
        if core_profession not in tops_celebs:
            tops_celebs.update({core_profession: []})
        curr_list_celebs = [x for x in all_celebs if x[2] == t]
        curr_list_celebs = [(x[0], x[1]) for x in curr_list_celebs]
        tops_celebs[core_profession].extend(curr_list_celebs)
    for c in tops_celebs:
        tops_celebs[c] = list(set(tops_celebs[c]))
        tops_celebs[c].sort(key=lambda x: x[1], reverse=True)
        tops_celebs[c] = tops_celebs[c][:300]
    return tops_celebs


def filter_entities(ent):
    query_term = {'query': {'bool': {'should': [
        {'terms': {'doc_title.keyword': [ent]}}]}},
        'sort': {'pageview': 'desc'}}
    results = query_es_index(es, ARTICLES_INDEX_NAME, query_term, size=MAX_ES_SEARCH_SIZE,
                             timeout=ANCHORTEXT_QUERY_TIMEOUT,
                             filter_path=['hits.hits._source.{}'.format(field) for field in FIELDS_FILTER])
    if len(results):
        return True
    return False


def run_test_es():
    ent = "Wrexham"

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


def filter_all_celebs():
    filtered_celeb = {}
    all_celeb_info = json.load(open("all_celeb_info.json"))

    for c in tqdm.tqdm(all_celeb_info):
        filtered_celeb.update({c: {}})
        for k in all_celeb_info[c]:
            if k != "pronoun" and k != "total_pg":
                filtered_celeb[c].update({k: []})
                for e in all_celeb_info[c][k]:
                    if filter_entities(e[0]):
                        filtered_celeb[c][k].append(e)
            else:
                filtered_celeb[c].update({k: all_celeb_info[c][k]})

    json.dump(filtered_celeb, open("filtered_celebs.json", "w+"))


if __name__ == "__main__":
    es = get_elasticsearch()
    # all_celebs = scrape_es()
    # pickle.dump(all_celebs, open("scraped_celebs.p", "wb+"))
    filter_all_celebs()

