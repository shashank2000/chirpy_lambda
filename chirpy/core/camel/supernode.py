import json
import random
import os
import traceback

from chirpy.core.camel.parser import parse
from chirpy.core.camel.predicate import Predicate, TruePredicate, FalsePredicate
from chirpy.core.camel.prompt import PromptList
from chirpy.core.camel.subnode import SubnodeList
from chirpy.core.camel.assignment import AssignmentList
from chirpy.core.camel.entities import EntityGroupList, EntityGroupRegexList
from dataclasses import dataclass, field, fields
from typing import List, Dict, Any

from importlib import import_module

import logging

logger = logging.getLogger("chirpylogger")


@dataclass
class Supernode:
    name: str
    subnodes: SubnodeList
    entry_conditions: Predicate = field(default_factory=TruePredicate)
    entry_locals: AssignmentList = field(default_factory=AssignmentList)
    prompts: PromptList = field(default_factory=PromptList)
    continue_conditions: Predicate = field(default_factory=TruePredicate)
    locals: AssignmentList = field(default_factory=AssignmentList)
    entry_conditions_takeover: Predicate = field(default_factory=FalsePredicate)
    set_state: AssignmentList = field(default_factory=AssignmentList)
    set_state_after: AssignmentList = field(default_factory=AssignmentList)
    entity_groups: EntityGroupList = field(default_factory=EntityGroupList)
    entity_groups_regex: EntityGroupRegexList = field(default_factory=EntityGroupRegexList)

    @classmethod
    def load(cls, camel_tree, name):
        initialization = {}
        for elem in camel_tree:
            key, item = elem
            assert any(
                field.name == key for field in fields(cls)
            ), f"Section {key} not found, options are {[x.name for x in fields(cls)]}"
            initialization[key] = item
        supernode = cls(name=name, **initialization)

        return supernode

    def __post_init__(self):
        name = self.name
        self.nlu = import_module(f"chirpy.symbolic_rgs.{name}.nlu")
        self.nlg_helpers = import_module(f"chirpy.symbolic_rgs.{name}.nlg_helpers")

    @classmethod
    def load_from_path(cls, path):
        BASE_PATH = os.path.join(os.path.dirname(__file__), "../../symbolic_rgs", path)
        with open(os.path.join(BASE_PATH, "supernode.camel"), "r") as f:
            camel_tree = parse(f.read())
        return cls.load(camel_tree, name=path)

    def get_flags(self, context):
        flags = self.nlu.get_flags(context)
        return flags

    def get_subnode_response(self, context, extra_subnodes=None):
        tried_subnodes = []
        while True:
            subnode = self.subnodes.select(
                context,
                extra_subnodes=extra_subnodes,
                not_ok_subnodes=tried_subnodes,
            )
            try:
                response = subnode.generate(context) + " "
                logger.primary_info(f"Received {response} from subnode {subnode}.")
                assert response is not None
                return subnode, response
            except Exception as e:
                logger.warning(f"Error in subnode:\n{traceback.format_exc()}")
                logger.bluejay(f"subnode_error//{subnode.name}: {traceback.format_exc()}", exc_info=True)
                tried_subnodes.append(subnode)
                continue

    def get_score(self, context):
        if len(self.prompts) == 0:
            return 0
        logger.warning(f"Kwargs are {context.kwargs}, self.name is {self.name}")
        if context.kwargs["prioritized_supernode"] == self.name:
            return int(1e10)
        if self.name == "LAUNCH":
            return 100
        return self.entry_conditions.get_score() + 1

    def __str__(self):
        return f"<{self.name}>"

    def __repr__(self):
        return f"<{self.name}>"


@dataclass
class SupernodeList:
    paths_to_supernodes: Dict[str, Supernode]

    @classmethod
    def from_paths(cls, paths):
        return cls(paths_to_supernodes=paths)

    @property
    def supernodes(self):
        logger.warning(f"Paths to supernodes are {type(x) for x in self.paths_to_supernodes.values()}")
        return list(self.paths_to_supernodes.values())

    def __getitem__(self, supernode_name):
        return self.paths_to_supernodes[supernode_name]

    def select(self, context):
        possible_supernodes = [
            (supernode, supernode.get_score(context))
            for supernode in self.supernodes
            if supernode.entry_conditions.evaluate(context, label=f"supernode_entry_conditions//{supernode.name}")
        ]
        logger.primary_info(
            f"Possible supernodes are: " + "; ".join(f"{supernode} (score={score})" for supernode, score in possible_supernodes)
        )
        logger.bluejay(
            f"supernodes: {json.dumps({supernode.name : {'score': score} for supernode, score in possible_supernodes})}"
        )
        supernodes, scores = zip(*possible_supernodes)
        logger.warning(f"Supernodes are {supernodes}, scores={scores}")
        next_supernode = random.choices(supernodes, weights=scores)[0]
        logger.bluejay(f"supernode_chosen: {next_supernode.name}")
        return next_supernode


def __main__():
    from pprint import pprint

    BASE_PATH = os.path.dirname(__file__)
    with open(os.path.join(BASE_PATH, "test1.camel"), "r") as f:
        camel_tree = parse(f.read())
    supernode = Supernode.load(camel_tree, name="test1")
    pprint(supernode, width=200)


if __name__ == "__main__":
    __main__()
()
