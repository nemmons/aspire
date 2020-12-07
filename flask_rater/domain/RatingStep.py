from abc import ABC, abstractmethod
from enum import Enum
from typing import List
from ..repo.RatingFactorRepository import AbstractRatingFactorRepository
from .RatingStepParameter import RatingStepParameter
from functools import reduce
from .RatingStepCondition import AbstractRatingStepCondition


class RatingStepType(Enum):
    ADD = 1
    SET = 2
    MULTIPLY = 3
    ROUND = 4
    LOOKUP = 5


class AbstractRatingStep(ABC):
    conditions: AbstractRatingStepCondition

    def __init__(self):
        pass

    def run(self, rating_variables: dict):
        if (not self.conditions) or self.conditions.check(rating_variables):
            return self.apply(rating_variables)
        return rating_variables

    @abstractmethod
    def apply(self, rating_variables: dict):
        pass


class Add(AbstractRatingStep):
    def __init__(self, target: str, parameters: List[RatingStepParameter], conditions: AbstractRatingStepCondition = None):
        super().__init__()
        self.target = target
        self.operands = parameters
        self.conditions = conditions

    def apply(self, rating_variables: dict):
        operands = map(lambda operand: float(operand.evaluate(rating_variables)), self.operands)
        result = reduce(lambda x, y: x+y, operands)

        rating_variables[self.target] = str(result)
        return rating_variables


class Multiply(AbstractRatingStep):
    def __init__(self, target: str, parameters: List[RatingStepParameter], conditions: AbstractRatingStepCondition = None):
        super().__init__()
        self.target = target
        self.operands = parameters
        self.conditions = conditions

    def apply(self, rating_variables: dict):
        operands = map(lambda operand: float(operand.evaluate(rating_variables)), self.operands)
        result = reduce(lambda x, y: x*y, operands)

        rating_variables[self.target] = str(result)
        return rating_variables


class Set(AbstractRatingStep):
    def __init__(self, target: str, parameters: List[RatingStepParameter], conditions: AbstractRatingStepCondition = None):
        super().__init__()
        self.target = target
        self.value = parameters[0]
        self.conditions = conditions

    def apply(self, rating_variables: dict):
        value = self.value.evaluate(rating_variables)
        rating_variables[self.target] = str(value)
        return rating_variables


class Round(AbstractRatingStep):
    def __init__(self, target: str, parameters: List[RatingStepParameter], conditions: AbstractRatingStepCondition = None):
        super().__init__()
        self.target = target
        self.value = parameters[0]
        self.places = parameters[1]
        self.conditions = conditions

    def apply(self, rating_variables: dict):
        decimal_places = self.places.evaluate(rating_variables)
        value_to_round = float(self.value.evaluate(rating_variables))
        rating_variables[self.target] = str(round(value_to_round, decimal_places))
        return rating_variables


class Lookup(AbstractRatingStep):
    def __init__(self, target: str, parameters: List[RatingStepParameter],
                 rating_factor_repository: AbstractRatingFactorRepository,
                 conditions: AbstractRatingStepCondition = None):
        super().__init__()
        self.target = target
        self.inputs = parameters
        self.rating_factor_repository = rating_factor_repository
        self.conditions = conditions

    def apply(self, rating_variables: dict):
        rating_factor_type = self.inputs.pop(0)
        rating_factor_type = rating_factor_type.evaluate(rating_variables)

        options = None
        if self.inputs[0].label == 'options':
            options = self.parse_options(self.inputs.pop(0).value)

        evaluated_inputs = {}
        for rating_step_parameter in self.inputs:
            evaluated_inputs[rating_step_parameter.label] = rating_step_parameter.evaluate(rating_variables)

        rating_variables[self.target] = self.rating_factor_repository.lookup(rating_factor_type, evaluated_inputs, options)
        return rating_variables

    def parse_options(self, options: str):
        parsed = options.split(',')
        options = {}
        for option_set in parsed:
            spl = option_set.split(':')
            options[spl[0]] = spl[1]
        return options
