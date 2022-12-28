import pickle

import requests
from bs4 import BeautifulSoup
import re
import json

from tqdm import tqdm


def call_search(sub):
    url = 'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'parse',
        'page': sub,
        'format': 'json',
        'prop': 'text',
        'redirects': ''
    }

    response = requests.get(url, params=params)
    data = response.json()

    try:
        raw_html = data['parse']['text']['*']
        sp = BeautifulSoup(raw_html, 'html.parser')
    except KeyError:
        return None
    return sp


def call_categories(sub):
    url = 'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'parse',
        'page': sub,
        'format': 'json',
        'prop': 'categories',
        'redirects': ''
    }

    response = requests.get(url, params=params)
    data = response.json()
    all_cats = [x['*'] for x in data['parse']['categories']]
    return "|".join(all_cats).lower()


def call_pageview(sub):
    url = 'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'query',
        'titles': sub.replace(" ", "_"),
        'format': 'json',
        'prop': 'pageviews',
    }

    response = requests.get(url, params=params)
    data = response.json()
    data = data['query']
    all_pv = data['pages'][list(data['pages'].keys())[0]]['pageviews'].values()
    all_pv = sum([0 if v is None else v for v in all_pv])
    return all_pv


def determine_pronouns(sub):
    all_cats = call_categories(sub)
    if "_male_" in all_cats:
        return "he"
    elif "_female_" in all_cats or "_actress" in all_cats:
        return "she"
    else:
        return "they"


def decide_work(cats):
    if "living_people" in cats:
        return False
    if "characters" in cats or "fictional" in cats:
        return True
    if "television_series" in cats or "television_shows" in cats or "tv_series" in cats or "tv" in cats:
        return True
    if "awards" in cats or "companies" in cats or "stations" in cats:
        return False
    if "lists" in cats or "genres" in cats or "navigational" in cats:
        return False
    if "films" in cats or "songs" in cats:
        return True
    return False


def extract_non_ref(soup):
    sp_text = soup.text
    # Jump to references
    if "References[edit]" in sp_text:
        ref_ind = sp_text.index("References[edit]")
        sp_text = sp_text[:ref_ind]
    else:
        sp_text = ""
    return sp_text



def extract_entities(subject):
    soup = call_search(subject)
    if soup is None:
        print("Incorrect Subject Entity!!")
    related_entities = []

    """
        Use the links to identify all wiki-linked entities
    """

    all_links = soup.find_all("a")
    for l in all_links:
        if "References" in str(l):
            print(l)
            break
        if "title" in l.attrs:
            related_entities.append(l.attrs['title'])
    print("Finished parsing initial list of entities for", subject)

    """
        Search up each of the entities, only find those with the subject name
    """
    related_entities = list(set(related_entities))
    celeb_dict = {
        "films": [],
        "songs": [],
        "tv": [],
        "characters": [],
        "pronoun": determine_pronouns(subject)
    }
    for e in tqdm(related_entities):
        e_sp = call_search(e)
        if e_sp is not None and "Award" not in e:
            all_cats = call_categories(e)
            if decide_work(all_cats):
                pv = call_pageview(e)
                if pv > 1000:
                    """
                        Check to make sure it is a song or a film or a TV show
                    """
                    e_text = extract_non_ref(e_sp)
                    matches_e = re.findall(subject, e_text)
                    total_nums = len(matches_e)

                    if total_nums >= 3:
                        if "people" in all_cats or "character" in all_cats:
                            celeb_dict['characters'].append((e, pv))
                        elif "songs" in all_cats:
                            celeb_dict['songs'].append((e, pv))
                        elif "films" in all_cats:
                            celeb_dict['films'].append((e, pv))
                        elif "television" in all_cats or "tv" in all_cats:
                            celeb_dict['tv'].append((e, pv))
    print("Finished final parsing for", subject)
    return celeb_dict


if __name__ == "__main__":
    # all_celebs = pickle.load(open("scraped_celebs.p", "rb"))
    all_celebs = ["Tom Cruise", "Nathan Fillion", "Ariana Grande", "Emma Watson"]
    master_celeb = {}
    for c in all_celebs:
        master_celeb.update({
            c.lower(): extract_entities(c)
        })
    print(master_celeb)
    json.dump(master_celeb, open("all_celeb_info.json", "w+"))

