from typing import List
from functools import reduce
from abc import ABC, abstractmethod
from .rating_step_parameter import RatingStepParameter


class AbstractRatingStepCondition(ABC):
    operator: str

    def __init__(self, operator: str, operands: List[__name__] = None):
        self.operator = operator
        self.operands = operands

    @abstractmethod
    def check(self, rating_variables):
        pass


class ComparisonOperation(AbstractRatingStepCondition):
    operands: List[RatingStepParameter]

    def check(self, rating_variables):
        operands = list(map(lambda operand: operand.evaluate(rating_variables), self.operands))

        if self.operator == '<':
            return float(operands[0]) < float(operands[1])
        if self.operator == '<=':
            return float(operands[0]) <= float(operands[1])
        if self.operator == '>':
            return float(operands[0]) > float(operands[1])
        if self.operator == '>=':
            return float(operands[0]) >= float(operands[1])
        if self.operator == '==':
            return operands[0] == operands[1]
        if self.operator == '!=':
            return operands[0] != operands[1]
        if self.operator == 'BETWEEN':
            return float(operands[1]) <= float(operands[0]) <= float(operands[2])

        return False

    def __str__(self):
        if not self.operands or not self.operator:
            return ''

        if self.operator == 'BETWEEN':
            return '(' + str(self.operands[0]) + ' BETWEEN ' + str(self.operands[1]) + ' AND ' + str(self.operands[2]) +')'

        padded = ' ' + self.operator + ' '
        return '(' + padded.join(str(o) for o in self.operands) + ')'


class LogicalOperation(AbstractRatingStepCondition):
    operands: List[AbstractRatingStepCondition]

    def check(self, rating_variables):
        results = list(map(lambda operation: operation.check(rating_variables), self.operands))

        if self.operator == 'AND':
            return reduce(lambda result1, result2: result1 and result2, results)
        if self.operator == 'OR':
            return reduce(lambda result1, result2: result1 or result2, results)
        if self.operator == 'NOT':
            return not results[0]
        return False

    def __str__(self):
        if not self.operands or not self.operator:
            return ''

        if self.operator == 'NOT':
            return '(' + self.operator + ' ' + str(self.operands[0]) + ')'

        padded = ' ' + self.operator + ' '
        return '(' + padded.join(str(o) for o in self.operands) + ')'
