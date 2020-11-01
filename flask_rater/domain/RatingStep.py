from abc import ABC, abstractmethod
from enum import Enum


class RatingStepParameterType(Enum):
    VARIABLE = 1
    LITERAL = 2


class RatingStepParameter:
    def __init__(self, value, rating_step_param_type: RatingStepParameterType):
        self.rating_step_param_type = rating_step_param_type
        self.value = value

    def evaluate(self, rating_variables: dict):
        if self.rating_step_param_type == RatingStepParameterType.VARIABLE:
            return rating_variables[self.value]
        elif self.rating_step_param_type == RatingStepParameterType.LITERAL:
            return self.value


class AbstractRatingStep(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def apply(self, rating_variables: dict):
        pass


class Add(AbstractRatingStep):
    def __init__(self, target: str, operand1: RatingStepParameter, operand2: RatingStepParameter):
        super().__init__()
        self.target = target
        self.operand1 = operand1
        self.operand2 = operand2

    def apply(self, rating_variables: dict):
        operand1 = float(self.operand1.evaluate(rating_variables))
        operand2 = float(self.operand2.evaluate(rating_variables))
        rating_variables[self.target] = operand1 + operand2
        return rating_variables


class Set(AbstractRatingStep):
    def __init__(self, target: str, value: RatingStepParameter):
        super().__init__()
        self.target = target
        self.value = value

    def apply(self, rating_variables: dict):
        value = self.value.evaluate(rating_variables)
        rating_variables[self.target] = value
        return rating_variables


# class Lookup(AbstractRatingStep):
#     inputs: list = None
#     target: str = None
#     rate_lookup_repository = None
#
#     def __init__(self, target, inputs, rate_lookup_repository):
#         super().__init__()
#         self.target = target
#         self.inputs = inputs
#         self.rate_lookup_repository = rate_lookup_repository
#
#     def apply(self, rating_variables: dict):
#         rating_variables[self.target] = self.rate_lookup_repository.lookup(self.inputs)
#         return rating_variables
