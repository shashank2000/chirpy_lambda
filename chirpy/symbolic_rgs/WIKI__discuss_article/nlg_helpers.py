from chirpy.core.entity_linker.entity_linker import WikiEntity
from chirpy.core.response_generator import nlg_helper
from chirpy.response_generators.wiki2 import wiki_utils


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


def construct_entitys_section_choices(entity: WikiEntity, sections, conj='and'):
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
def entitys_section_choices(entity: WikiEntity, sections):
    _, entitys_section_choices = construct_entitys_section_choices(entity, sections)
    return wiki_utils.clean_wiki_text(entitys_section_choices)