from typing import List
from dataclasses import dataclass

from chirpy.core.camel.predicate import Predicate
from chirpy.core.camel.nlg import NLGNode

@dataclass
class Prompt:
	name : str
	entry_conditions : Predicate
	response : NLGNode

@dataclass
class PromptList:
	prompts : List[Prompt]