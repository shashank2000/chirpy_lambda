from chirpy.core.entity_linker.entity_linker import WikiEntity
from chirpy.core.response_generator import nlg_helper
from chirpy.core.util import filter_and_log
from chirpy.response_generators.wiki2 import wiki_utils
from chirpy.response_generators.wiki2.wiki_utils import WikiSection
from typing import List
import random

import logging
logger = logging.getLogger('chirpylogger')

def is_plural(sections):
    return len(sections) >= 2


@nlg_helper
def them_it(sections):
    return "either of them" if is_plural(sections) else "it"


@nlg_helper
def is_are(sections):
    return "are" if is_plural(sections) else "is"


def sanitize_section_title(section, entity: WikiEntity):
    """
    Examples:
    singing animals, singing -> singing animals
    history, philosophy -> history
    history of philosophy, philosophy -> the history of philosophy
    """
    if entity in section:
        if section.endswith(entity): #branches of philosophy
            section = "the " + section
        else: # e.g. singing animals
            pass
    return section


def construct_entitys_section_choices(entity: str, sections: List[str], conj='and'):
    """
    Constructs the exact phrasing for section_choices and entitys_section_choices,
    so that we avoid phrases like "Philosophy's history of philosophy" or "Singing's singing animals"
    :param sections:
    :return:
    """
    plural = len(sections) >= 2
    entitys = f"{entity}'s"
    if plural:
        section_1 = sections[0]
        section_2 = sections[1]
        section_choices = f"{section_1} {conj} {section_2}"
        if entity in section_choices: # Singing -> singing animals, Philosophy -> branches of philosophy
            section_1 = sanitize_section_title(section_1, entity)
            section_2 = sanitize_section_title(section_2, entity)
            entitys_section_choices = f"{section_1} {conj} {section_2}"
        else:
            entitys_section_choices = f"{entitys} {section_choices}"
    else:
        section_choices = f"{sections[0]}"
        if entity in section_choices:
            entitys_section_choices = sanitize_section_title(section_choices, entity)
        else:
            entitys_section_choices = f"{entitys} {section_choices}"
    return section_choices, entitys_section_choices


@nlg_helper
def get_sections(entity: WikiEntity, suggested_sections: List[WikiSection], discussed_sections: List[WikiSection], last_discussed_section: WikiSection):
    sections = wiki_utils.get_wiki_sections(entity.name)
    print("SECTOPMS", sections)
    valid_sections = filter_and_log(lambda section: section not in suggested_sections, sections,
                                        'Wiki Section', reason_for_filtering='these sections were suggested')
    valid_sections = filter_and_log(lambda section: section not in discussed_sections, valid_sections,
                                        'Wiki Section', reason_for_filtering='these sections were discussed')

    # Suggest level 2 sections if that's what we should be doing
    if last_discussed_section is not None:
        logger.primary_info("Last discussed section is not None")
        # First check if there are subsections of the last discussed section
        # For that we would need it to be level 1 section
        if last_discussed_section.level() == 1:
            subsections = list(
                filter(lambda section: section.is_descendant_of(last_discussed_section), valid_sections))
            if subsections:
                return subsections
                # text = self.choose(subsection_prompts(entity.talkable_name, last_discussed_section.title, chosen_section_titles, repeat=repeat or False))
            logger.info(f"No more unused subsections of level 1 section {last_discussed_section.title}. Not suggesting more subsections")

        if last_discussed_section.level() == 2:
            parent_section = last_discussed_section.ancestor_titles[-1]

            # Get all siblings of the section
            siblings = list(
                filter(lambda section: section.ancestor_titles and section.ancestor_titles[-1] == parent_section,
                        sections))

            # Don't suggest any more siblings if 2 have already been discussed, as a simplifying assumption
            valid_siblings = list(set(siblings) & set(valid_sections))
            if len(set(siblings) & set(discussed_sections)) < 2 and valid_siblings:
                return valid_siblings
                # text = self.choose(subsection_prompts(entity.talkable_name, parent_section, chosen_section_titles, repeat=repeat or True))
            logger.info(f"One more sibling of {parent_section} has already been discussed. Not suggesting more sibling subsections.")
    
    first_level_sections = list(filter(lambda section: section.level() == 1, valid_sections))

    # If not, suggest level 1 sections
    # this can happen if sections have been suggested before,
    # or we haven't been able to suggest any 2nd level sections to suggest
    if first_level_sections:
        logger.primary_info(
            f"Choosing from {[s.title for s in first_level_sections]} 1st level sections")
        return first_level_sections
        # text = self.choose(section_prompt_text(entity.talkable_name, [s.title for s in chosen_sections], repeat=have_response or repeat or last_discussed_section is not None))
    logger.info("No more unused 1st level sections left to choose from")

    # All valid sections are 2nd level now
    # but, second level section titles can feel disconnected, so
    # suggest two 2nd level sections but read out their first level section titles
    first_level_section_titles = set([section.ancestor_titles[-1] for section in valid_sections])
    # if 2 or more children of the first level section headings have been discussed, remove it
    filtered_first_level_section_titles = filter_and_log(lambda f_section_title:
                                                            len([s for s in discussed_sections if (
                                                                        s.level() >= 2 and s.ancestor_titles[
                                                                    -1] == f_section_title) or s.title == f_section_title]) <= 3,
                                                            first_level_section_titles, 'first level sections',
                                                            reason_for_filtering='either the section overview or their children have been discussed at least three times in the past')
    
    if filtered_first_level_section_titles:
        return filtered_first_level_section_titles
        # text = self.choose(section_prompt_text(entity.talkable_name, chosen_first_level_section_titles, repeat=have_response or repeat or last_discussed_section is not None))
    
    logger.primary_info(f"No more useful sections left for entity: {entity.name}")
    return [] # TODO: Make sure this doesn't create a bug


@nlg_helper
def choose_from_sections(sections: List[WikiSection]):
    """
    Returns two sections that don't contain "and" or a single section that contains an "and".
    Note that we construct this function this way, so as to avoid downstream phrases like:
    "(Etymology and terminology) and (Personal life and background)"
    :param sections: either List[str] or List[WikiSection]
    :param k:
    :return:
    """
    # TODO-later: Make this a multi armed bandit for recommendations
    # TODO merge sections with the same name
    logger.primary_info(f"Wiki sections being chosen from: {[s.title for s in sections]}")
    chosen_sections = []
    try:
        if isinstance(sections[0], WikiSection):
            sections = list({s.title: s for s in sections[::-1]}.values())
            random.shuffle(sections)
            # logger.primary_info(f"titles are {[s.title for s in sections]}")
            s_and = [s for s in sections if "and" in s.title.split()]
            s_no_and = [s for s in sections if "and" not in s.title.split()]
        else: # List[str]
            sections = list(set(sections))
            random.shuffle(sections)
            s_and = [s for s in sections if "and" in s.split()]
            s_no_and = [s for s in sections if "and" not in s.split()]
            
        if len(s_no_and) >= 2:
            chosen_sections = s_no_and[:2]

        elif len(s_and) >= 1:
            chosen_sections = [s_and[0]]

        else:
            chosen_sections = [s_no_and[0]]
    except ValueError:
        chosen_sections = sections
    chosen_sections_titles = [s.title for s in chosen_sections]
    logger.primary_info(f"Chose {chosen_sections_titles} to suggest.")
    return chosen_sections_titles


@nlg_helper
def entitys_section_choices(entity: WikiEntity, chosen_sections_titles: List[str]):
    _, entitys_section_choices = construct_entitys_section_choices(entity.talkable_name, chosen_sections_titles)
    return wiki_utils.clean_wiki_text(entitys_section_choices)