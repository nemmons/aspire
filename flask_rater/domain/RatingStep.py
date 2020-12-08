from abc import ABC, abstractmethod
from enum import IntEnum
from typing import List
from ..repo.RatingFactorRepository import AbstractRatingFactorRepository
from .RatingStepParameter import RatingStepParameter
from functools import reduce
from .RatingStepCondition import AbstractRatingStepCondition
import operator


class RatingStepType(IntEnum):
    SET = 1
    ADD = 2
    SUBTRACT = 3
    MULTIPLY = 4
    DIVIDE = 5
    ROUND = 6
    LOOKUP = 7
    LINEAR_INTERPOLATE = 8


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


class BaseArithmeticRatingStep(AbstractRatingStep):
    operation: operator

    def __init__(self, target: str, parameters: List[RatingStepParameter], conditions: AbstractRatingStepCondition = None):
        super().__init__()
        self.target = target
        self.operands = parameters
        self.conditions = conditions

    def evaluate_operands(self, rating_variables: dict):
        return map(lambda operand: float(operand.evaluate(rating_variables)), self.operands)

    def apply(self, rating_variables: dict):
        operands = self.evaluate_operands(rating_variables)
        result = reduce(lambda x, y: self.operation(x, y), operands)

        rating_variables[self.target] = str(result)
        return rating_variables


class Add(BaseArithmeticRatingStep):
    operation = operator.add


class Subtract(BaseArithmeticRatingStep):
    operation = operator.sub


class Multiply(BaseArithmeticRatingStep):
    operation = operator.mul


class Divide(BaseArithmeticRatingStep):
    operation = operator.truediv


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
        decimal_places = int(self.places.evaluate(rating_variables))
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


class LinearInterpolate(AbstractRatingStep):
    def __init__(self, target: str, parameters: List[RatingStepParameter],
                 rating_factor_repository: AbstractRatingFactorRepository,
                 conditions: AbstractRatingStepCondition = None):
        self.target = target
        self.params = parameters
        self.rating_factor_repository = rating_factor_repository
        self.conditions = conditions
        super().__init__()

    def apply(self, rating_variables: dict):
        rating_factor_type = self.params.pop(0)
        rating_factor_type = rating_factor_type.evaluate(rating_variables)

        options = None
        if self.params[0].label == 'options':
            options = self.parse_options(self.params.pop(0).value)

        interpolate_variable = options['interpolate']
        interpolate_column = None

        evaluated_params = {}
        x = None
        for rating_step_parameter in self.params:
            param = rating_step_parameter.evaluate(rating_variables)
            evaluated_params[rating_step_parameter.label] = param
            if rating_step_parameter.value == interpolate_variable:
                x = param
                interpolate_column = rating_step_parameter.label

        if x is None:
            raise Exception("Missing input for interpolation")

        lower = self.rating_factor_repository.get_factor(
            rating_factor_type,
            evaluated_params.copy(),
            {"step_down": interpolate_column}
        )
        if lower is None:
            raise Exception("Interpolation Lookup failed to find lower value!")
        upper = self.rating_factor_repository.get_factor(
            rating_factor_type,
            evaluated_params.copy(),
            {"step_up": interpolate_column}
        )
        if upper is None:
            raise Exception("Interpolation Lookup failed to find upper value!")

        x = float(x)
        x0 = float(getattr(lower, interpolate_column))
        x1 = float(getattr(upper, interpolate_column))
        y0 = float(lower.value)
        y1 = float(upper.value)

        if x == x0:
            y = y0
        elif x == x1:
            y = y1
        else:
            y = y0 + ((y1 - y0) / (x1 - x0) * (x - x0))

        rating_variables[self.target] = str(y)
        return rating_variables

    def parse_options(self, options: str):
        parsed = options.split(',')
        options = {}
        for option_set in parsed:
            spl = option_set.split(':')
            options[spl[0]] = spl[1]
        return options

