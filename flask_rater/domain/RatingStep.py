from abc import ABC, abstractmethod
from enum import Enum
from typing import List
from .RatingStepParameter import RatingStepParameter
from functools import reduce


class RatingStepType(Enum):

    ADD = 1
    SET = 2
    MULTIPLY = 3
    ROUND = 4


class AbstractRatingStep(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def apply(self, rating_variables: dict):
        pass


class Add(AbstractRatingStep):
    def __init__(self, target: str, parameters: List[RatingStepParameter]):
        super().__init__()
        self.target = target
        self.operands = parameters

    def apply(self, rating_variables: dict):
        operands = map(lambda operand: float(operand.evaluate(rating_variables)), self.operands)
        result = reduce(lambda x, y: x+y, operands)

        rating_variables[self.target] = str(result)
        return rating_variables


class Multiply(AbstractRatingStep):
    def __init__(self, target: str, parameters: List[RatingStepParameter]):
        super().__init__()
        self.target = target
        self.operands = parameters

    def apply(self, rating_variables: dict):
        operands = map(lambda operand: float(operand.evaluate(rating_variables)), self.operands)
        result = reduce(lambda x, y: x*y, operands)

        rating_variables[self.target] = str(result)
        return rating_variables


class Set(AbstractRatingStep):
    def __init__(self, target: str, parameters: List[RatingStepParameter]):
        super().__init__()
        self.target = target
        self.value = parameters[0]

    def apply(self, rating_variables: dict):
        value = self.value.evaluate(rating_variables)
        rating_variables[self.target] = str(value)
        return rating_variables


class Round(AbstractRatingStep):
    def __init__(self, target: str, parameters: List[RatingStepParameter]):
        super().__init__()
        self.target = target
        self.value = parameters[0]
        self.places = parameters[1]

    def apply(self, rating_variables: dict):
        decimal_places = self.places.evaluate(rating_variables)
        value_to_round = float(self.value.evaluate(rating_variables))
        rating_variables[self.target] = str(round(value_to_round, decimal_places))
        return rating_variables
