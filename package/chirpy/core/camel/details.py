from typing import Dict
from dataclasses import dataclass, field
from chirpy.core.camel.variable import Variable

import logging

logger = logging.getLogger("chirpylogger")


@dataclass
class DetailList:
    details: Dict[str, Variable] = field(default_factory=dict)

    def __getitem__(self, key):
        return self.details.get(key, None)
