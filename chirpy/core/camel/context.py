from dataclasses import dataclass
from typing import Dict

@dataclass
class Context:
	supernode : "Supernode"
	state : "State"
	flags : Dict
	state : Dict
	utilities : Dict

