from typing import List
from dataclasses import dataclass

from chirpy.core.camel.assignment import AssignmentList
from chirpy.core.camel.predicate import Predicate
from chirpy.core.camel.nlg import NLGNode
from chirpy.core.camel.attribute import AttributeList

import json
import random

import logging

logger = logging.getLogger("chirpylogger")


@dataclass
class Subnode:
    name: str
    entry_conditions: Predicate
    response: NLGNode
    set_state: AssignmentList
    attributes: AttributeList

    def generate(self, context):
        logger.primary_info(f"Subnode {self.name} is generating.")
        return self.response.generate(context)

    def __str__(self):
        return "<<" + self.name + ">>"

    def __repr__(self):
        return self.__str__()


@dataclass
class SubnodeGroup:
    subnodes: List[Subnode]

    def select(self, context, all_possible_subnodes):
        possible_subnodes = [
            subnode
            for subnode in self.subnodes
            if subnode.entry_conditions.evaluate(context, label=f"subnode_entry_conditions//{subnode.name}")
        ]
        if not len(possible_subnodes):
            return None

        all_possible_subnodes.extend(possible_subnodes)

        # return a possible subnode
        return random.choice(possible_subnodes)


def choose_subnodes(subnodes):
    def get_score_of_subnode(subnode):
        score = 0
        if subnode.attributes["force_activation"]:
            score += 100
        return score

    subnodes = [(subnode, get_score_of_subnode(subnode)) for subnode in subnodes]
    subnodes = sorted(subnodes, key=lambda x: x[1], reverse=True)
    logger.primary_info(f"Subnodes with scores: {subnodes}")

    return subnodes[0][0]


@dataclass
class SubnodeList:
    groups: List[SubnodeGroup]

    def select(self, context, extra_subnodes=None, not_ok_subnodes=[]):
        all_possible_subnodes = []
        subnodes = [group.select(context, all_possible_subnodes) for group in self.groups]
        if extra_subnodes:
            subnodes += [group.select(context, all_possible_subnodes) for group in extra_subnodes.groups]
        possible_subnodes = [subnode for subnode in subnodes if subnode is not None and subnode not in not_ok_subnodes]

        logger.primary_info(f"Possible subnodes are: {all_possible_subnodes}")
        logger.bluejay(f"subnodes: {json.dumps({node.name: {'available': True} for node in all_possible_subnodes})}")
        assert len(possible_subnodes), "No subnode found!"

        chosen_subnode = choose_subnodes(possible_subnodes)

        logger.bluejay(f"subnodes_chosen: {chosen_subnode.name}")

        # return the first possible subnode
        return chosen_subnode
