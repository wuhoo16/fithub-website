from abc import ABC, abstractmethod

# Note that ModelInterface is an abstract base class = Python's version of an interface

class ModelObjInterface(ABC):
    def __init__(self, **kwargs):
        pass

    def to_dictionary(self):
        pass
    
    def __str__(self):
        pass