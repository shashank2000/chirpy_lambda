PIPES = {}

def pipe(func):
	PIPES[func.__name__] = func
	
def get_pipe(pipe_name):
	return PIPES[pipe_name]

@pipe
def talkable(ent : "WikiEntity"):
	return ent.talkable_name
	
@pipe
def name(ent : "WikiEntity"):
	return ent.name
	
@pipe
def lower(s : str):
	return s.lower()	
	
@pipe
def increment(i : int):
	assert isinstance(i, int)
	return i + 1
