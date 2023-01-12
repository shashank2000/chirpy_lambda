from typing import List
from dataclasses import dataclass, field

import logging
logger = logging.getLogger('chirpylogger')

@dataclass
class AttributeList:
	attributes : List[str] = field(default_factory=list)
	
	def __getitem__(self, val):
		return (val in self.attributes)
		
	def __str__(self):
		return "<<" + ",".join(self.attributes) + ">>"