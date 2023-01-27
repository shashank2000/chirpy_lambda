from dataclasses import dataclass, field
from typing import List

from chirpy.core.entity_linker.entity_groups import EntityGroup as EntityLinkerGroup, EntityGroupsForExpectedType
from chirpy.core.regex.regex_template import RegexTemplate
from chirpy.core.response_generator.helpers import global_templates_cache


@dataclass
class EntityGroup():
	entityGroup : EntityLinkerGroup
	def __init__(self, entityGroupName: str) -> None:
		self.entityGroup = getattr(EntityGroupsForExpectedType, entityGroupName)
	def evaluate(self, context):
		if not context.utilities["cur_entity"]:
			return False
		return self.entityGroup.matches(context.utilities["cur_entity"])

@dataclass
class EntityGroupRegex():
	entityRegex : RegexTemplate
	def __init__(self, entityRegexName: str) -> None:
		self.entityRegex = global_templates_cache[entityRegexName]
	def evaluate(self, context):
		slots = self.entityRegex.execute(context.utterance)
		return bool(slots)

@dataclass
class EntityGroupList():
	entityGroups : List[EntityGroup] = field(default_factory=list)
	def evaluate(self, context, label=""):
		for entity in self.entityGroups:
			if entity.evaluate(context):
				return True
		return False
	def get_score(self):
		return 1

@dataclass
class EntityGroupRegexList():
	entityRegexes : List[EntityGroupRegex] = field(default_factory=list)
	def evaluate(self, context, label=""):
		for entity in self.entityRegexes:
			if entity.evaluate(context):
				return True
		return False