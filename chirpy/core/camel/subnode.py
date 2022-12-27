from typing import List
from dataclasses import dataclass

from chirpy.core.camel.predicate import Predicate
from chirpy.core.camel.nlg import NLGNode

@dataclass
class Subnode:
	name : str
	entry_conditions : Predicate
	response : NLGNode

@dataclass
class SubnodeList:
	subnodes : List[Subnode]
