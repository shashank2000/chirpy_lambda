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

def get():
    #     piano_compositions = ['Piano compositions by American composers',
#                             'Piano compositions by Austrian composers',
#                             'Piano compositions by French composers',
#                             'Piano compositions by German composers',
#                             'Piano compositions by Hungarian composers',
#                             'Piano compositions by Polish composers',
#                             'Piano compositions by Russian composers',
#                             'Preludes by Johann Sebastian Bach',
#                             'Piano sonatas by Johannes Brahms',
#                             'Concertante works by Frédéric Chopin',
#                             'Études by Frédéric Chopin',
#                             'Mazurkas by Frédéric Chopin',
#                             'Nocturnes by Frédéric Chopin',
#                             'Piano sonatas by Frédéric Chopin',
#                             'Polonaises by Frédéric Chopin',
#                             'Waltzes by Frédéric Chopin',
#                             'Preludes by Claude Debussy',
#                             'Compositions for piano by He Xuntian',
#                             'Piano music by John Ireland',
#                             'Concertos by Franz Liszt',
#                             'Études by Franz Liszt',
#                             'Hungarian Rhapsodies by Franz Liszt',
#                             'Piano music by Franz Schubert',
#                             'Piano music by Robert Schumann',
#                             'Piano sonatas by Alexander Scriabin',
#                             'Preludes by Alexander Scriabin',
#                             'Compositions for piano']
    piano_and_violin_compositions = ['Alt-Wiener Tanzweisen', 'Ballade (Dvořák)', 'Duo Concertant', 'Fantasy for violin and piano (Schubert)',
                                    'Morceaux de salon, Op. 6 (Rachmaninoff)', 'Myths (Szymanowski)', 'Nocturne and Tarantella (Szymanowski)',
                                    'Nocturne in B major (Dvořák)', 'Polonaise de Concert, Op. 4 (Wieniawski)', 'Praeludium and Allegro',
                                    'Romance in F minor (Dvořák)', 'Romantic Pieces (Dvořák)', 'Rondo in B minor for violin and piano, D 895 (Schubert)',
                                    'Ruralia hungarica', 'Slavonic Dances', 'Souvenir d&#039;un lieu cher', 'Spanish Dances',
                                    'Three Romances for Violin and Piano', 'Zigeunerweisen']
    violin_compositions =["Compositions for violin"]

def scrape_es():
    es = get_elasticsearch()
    # https://en.wikipedia.org/wiki/Category:Singing

    all_temps_categories = []
    all_temps_wiki_categories = ['musical work']
    all_music_pieces = set()
    for t in all_temps_categories:
        query = {'query': {'bool': {"must": [{'terms': {'categories.keyword': [t]}}]}},
                 'sort': {'pageview': 'desc'}}
        results = query_es_index(es, ARTICLES_INDEX_NAME, query, size=MAX_ES_SEARCH_SIZE,
                                 timeout=ANCHORTEXT_QUERY_TIMEOUT,
                                 filter_path=['hits.hits._source.{}'.format(field) for field in FIELDS_FILTER])
        for s in results:
            all_music_pieces.add(s['_source']['doc_title'])

    for t in all_temps_wiki_categories:
        query = {'query': {'bool': {"must": [{'terms': {'wikidata_categories_all.keyword': [t]}}]}},
                'sort': {'pageview': 'desc'}}
        results = query_es_index(es, ARTICLES_INDEX_NAME, query, size=MAX_ES_SEARCH_SIZE,
                                 timeout=ANCHORTEXT_QUERY_TIMEOUT,
                                 filter_path=['hits.hits._source.{}'.format(field) for field in FIELDS_FILTER])
        for s in results:
            all_music_pieces.add(s['_source']['doc_title'])
            print(s['_source']['doc_title'])
    print(len(all_music_pieces))    # 15146 entities
    return all_music_pieces

if __name__ == "__main__":
    all_singers = scrape_es()
    #pickle.dump(all_singers, open("scraped_music_pieces.p", "wb+"))
