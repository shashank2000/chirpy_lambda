from dataclasses import dataclass, field
from typing import List

from chirpy.core.entity_linker.entity_groups import EntityGroup as _EntityGroup, EntityGroupsForExpectedType
from chirpy.core.regex.regex_template import RegexTemplate
from chirpy.core.response_generator.helpers import global_templates_cache


@dataclass
class EntityGroup():
	entityGroup : _EntityGroup
	def __init__(self, entityGroupName: str) -> None:
		self.entityGroup = getattr(EntityGroupsForExpectedType, entityGroupName)
	def evaluate(self, context):
		if not context.flags["GlobalFlag__SpecifiedEntity"]:
			return False
		return self.entityGroup.matches(context.flags["GlobalFlag__SpecifiedEntity"])

@dataclass
class EntityGroupRegex():
	entityRegex : RegexTemplate
	def __init__(self, entityRegexName: str) -> None:
		self.entityRegex = global_templates_cache[entityRegexName]
	def evaluate(self, context):
		slots = self.entityRegex.execute(context.utterance)
		if not slots:
			return False
		return True

@dataclass
class EntityGroupList():
	entityGroups : List[EntityGroup] = field(default_factory=list)
	def evaluate(self, context):
		for entity in self.entityGroups:
			if entity.evaluate(context):
				return True
		return False

@dataclass
class EntityGroupRegexList():
	entityRegexes : List[EntityGroupRegex] = field(default_factory=list)
	def evaluate(self, context):
		for entity in self.entityRegexes:
			if entity.evaluate(context):
				return True
		return False