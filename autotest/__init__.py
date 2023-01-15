## A BluejayAgent must be started at localhost:8765.

from enum import IntEnum
from requests.exceptions import JSONDecodeError
import requests
import json
import os

import pytest


class ImportanceLevel(IntEnum):
    ACUTE = 10
    BAD = 5
    WARNING = 3
    BASE = 2
    DEBUG = 1


CHIRPY_PATH = "localhost:8765"


class Chirpy:
    def __init__(self):
        self.attributes = {}
        self.reset_hard()

    def run(self, utterance, reset=False, **kwargs):
        result = requests.get(
            "http://localhost:8765/api/ping",
            params={"input": utterance, "reset": reset, "kwargs": json.dumps(kwargs)},
        )
        self.attributes = result.json()

    def reset_hard(self):
        self.run("", reset=True)

    def reset_soft(self):
        try:
            self.run("!!reset !")
        except JSONDecodeError:
            self.reset_hard()

    def __getattr__(self, attr):
        if attr in self.attributes:
            return self.attributes[attr]
        raise AttributeError(f"Attribute {attr} was not dumped.")

    def get_attributes(self):
        return self.attributes.keys()


CHIRPY = Chirpy()

NAME = "Chris"


class BaseIntegrationTest:
    def startup_bot(self, launch_script=False, **kwargs):
        CHIRPY.reset_soft()
        if launch_script:
            CHIRPY.run(NAME, **kwargs)
        return CHIRPY
