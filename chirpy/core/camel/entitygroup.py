from dataclasses import dataclass, field
from typing import List

from chirpy.core.entity_linker.entity_groups import EntityGroup as _EntityGroup, EntityGroupsForExpectedType


@dataclass
class EntityGroup():
		entityGroup : _EntityGroup
		def __init__(self, entityGroupName: str) -> None:
				self.entityGroup = getattr(EntityGroupsForExpectedType, entityGroupName)
		def evaluate(self, context):
				if not context.utilities["cur_entity"]:
						return False
				return self.entityGroup.matches(context.utilities["cur_entity"])

@dataclass
class EntityGroupList():
		entityGroups : List[_EntityGroup] = field(default_factory=list)
		def evaluate(self, context):
				for entity in self.entityGroups:
						if entity.evaluate(context):
								return True
				return False