PIPES = {}


class PseudoEntity:
    def __init__(self, data):
        self.name = data
        self.talkable_name = ""

    def lower(self):
        return ""


def pipe(func):
    PIPES[func.__name__] = func


def get_pipe(pipe_name):
    return PIPES[pipe_name]


@pipe
def talkable(ent: "WikiEntity"):
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
def name(ent: "WikiEntity"):
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
