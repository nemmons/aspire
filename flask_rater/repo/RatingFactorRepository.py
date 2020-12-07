from abc import ABC, abstractmethod


class AbstractRatingFactorRepository(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def lookup(self, rating_factor_type: str, params: dict, options=None):
        pass

    @abstractmethod
    def get_factor(self, rating_factor_type: str, params: dict, options=None):
        pass