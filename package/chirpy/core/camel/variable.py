from dataclasses import dataclass

from chirpy.core.response_generator.nlu import ALL_FLAGS


@dataclass
class Variable:
    namespace: str
    name: str

    def __post_init__(self):
        if self.namespace == "Flags":
            assert self.name in ALL_FLAGS, f"Flags.{self.name} isn't defined in ALL_FLAGS!"

    def generate(self, context):
        assert hasattr(context, self.namespace.lower()), f"Namespace {self.namespace} not found!"
        namespace = getattr(context, self.namespace.lower())
        return getattr(context, self.namespace.lower())[self.name]

    def __str__(self):
        return f"{self.namespace}.{self.name}"
