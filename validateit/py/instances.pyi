from . import abstract

def add(alias: str, instance: abstract.Validator) -> abstract.Validator: ...
def put(alias: str, instance: abstract.Validator) -> abstract.Validator: ...
def get(alias: str) -> abstract.Validator: ...
def clear() -> None: ...
