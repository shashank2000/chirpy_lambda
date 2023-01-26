import re
import inflect
engine = inflect.engine()

PIPES = {}


class PseudoEntity:
    def __init__(self, data):
        self.name = data
        self.talkable_name = data

    def __str__(self):
        return f"PseudoEntity<{self.name}>"

    def lower(self):
        return ""
    
    @property
    def common_name(self) -> str:
        """
        Returns the title, with any bracketed parts removed. While self.name is the full wikipedia article title
        (e.g. "Frozen (2013 film)"), common_name is just "Frozen".

        Note: this function used to return the most common anchortext for this entity, but that had some difficulties
        e.g. with the anchortext being an adjective e.g. "atheist" for "Atheism", plus other problems.
        """
        # return next(iter(self.anchortext_counts))
        return re.sub("\(.*?\)", "", self.name).strip()
    
    @property
    def is_plural(self) -> bool:
        #logger.warning(f"Talkable name is {self.talkable_name}")
        #logger.warning(f"Is singular is {engine.singular_noun(self.talkable_name)}")
        return bool(engine.singular_noun(self.talkable_name))


def pipe(func):
    PIPES[func.__name__] = func


def get_pipe(pipe_name):
    return PIPES[pipe_name]


@pipe
def talkable(ent: PseudoEntity):
    if ent is None:
        return ""
    return ent.talkable_name


@pipe
def topseudoentity(data):
    """Converts data to an object obj where obj.name = data or None if data is None"""
    if data is None:
        return None
    return PseudoEntity(data)


@pipe
def name(ent: PseudoEntity):
    if ent is None:
        return ""
    return ent.name


@pipe
def lower(s: str):
    return s.lower()


@pipe
def increment(i: int):
    assert isinstance(i, int)
    return i + 1


@pipe
def is_are(l: list):
    return "is" if len(l) == 1 else "are"


@pipe
def them_it(l: list):
    return "it" if len(l) == 1 else "them"
