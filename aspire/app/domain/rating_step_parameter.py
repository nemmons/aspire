from enum import IntEnum


class RatingStepParameterType(IntEnum):
    VARIABLE = 1
    LITERAL = 2


class RatingStepParameter:
    def __init__(self, label: str, value, parameter_type: RatingStepParameterType):
        self.label = label
        self.parameter_type = parameter_type
        self.value = value

    def evaluate(self, rating_variables: dict):
        if self.parameter_type == RatingStepParameterType.VARIABLE:
            return rating_variables[self.value]
        if self.parameter_type == RatingStepParameterType.LITERAL:
            return self.value

    def __str__(self):
        return self.label
