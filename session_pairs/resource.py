from abc import ABC, abstractmethod

class Resource(ABC):
    def __init__(self):
        self.model: object

    @abstractmethod
    def reset(self):
        pass