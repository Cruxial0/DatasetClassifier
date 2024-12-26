from typing import Callable

class UpdatePoller:
    def __init__(self):
        self.updates: dict[str, Callable] = {}

    def add_method(self, name: str, method: Callable):
        self.updates[name] = method

    def poll_update(self, name: str, *args, **kwargs):
        self.updates[name](*args, **kwargs)