from abc import ABC, abstractmethod
from database.models import RatingManual as RatingManualModel, RatingStep as RatingStepModel, \
    RatingStepParameter as RatingStepParameterModel
from domain import RatingManual, RatingStep
from sqlalchemy.orm import session, joinedload
from repo.RatingFactorRepository import RatingFactorRepository
from typing import List
import json
from domain.RatingStepCondition import LogicalOperation, ComparisonOperation
from domain.RatingStepParameter import RatingStepParameter, RatingStepParameterType


class AbstractRatingManualRepository(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def get(self, rating_manual_id):
        pass

    @abstractmethod
    def store(self, rating_manual_id=None):
        pass


class RatingManualRepository(AbstractRatingManualRepository):

    def __init__(self, db_session):
        super().__init__()
        self.db_session = db_session

    def get(self, rating_manual_id):
        manual = self.db_session.query(RatingManualModel). \
            filter(RatingManualModel.id == rating_manual_id). \
            options(joinedload(RatingManualModel.rating_steps).joinedload(RatingStepModel.rating_step_parameters)). \
            one()

        rating_steps = []
        for rating_step in manual.rating_steps:
            rating_steps.append(self.factory_rating_step(rating_step, rating_manual_id))

        rating_manual = RatingManual.RatingManual(manual.name, manual.description, rating_steps)

        return rating_manual

    def store(self, rating_manual_id=None):
        pass

    def factory_rating_step(self, data: RatingStepModel, rating_manual_id: int):
        rating_step_type = RatingStep.RatingStepType(data.rating_step_type_id)

        params = self.create_rating_step_parameters(data.rating_step_parameters)
        conditions = self.create_rating_step_conditions(data.conditions)

        if rating_step_type == RatingStep.RatingStepType.SET:
            step = RatingStep.Set(data.target, params, conditions)
        elif rating_step_type == RatingStep.RatingStepType.ADD:
            step = RatingStep.Add(data.target, params, conditions)
        elif rating_step_type == RatingStep.RatingStepType.SUBTRACT:
            step = RatingStep.Subtract(data.target, params, conditions)
        elif rating_step_type == RatingStep.RatingStepType.MULTIPLY:
            step = RatingStep.Multiply(data.target, params, conditions)
        elif rating_step_type == RatingStep.RatingStepType.DIVIDE:
            step = RatingStep.Divide(data.target, params, conditions)
        elif rating_step_type == RatingStep.RatingStepType.ROUND:
            step = RatingStep.Round(data.target, params, conditions)
        elif rating_step_type == RatingStep.RatingStepType.LOOKUP:
            step = RatingStep.Lookup(data.target, params, RatingFactorRepository(rating_manual_id, self.db_session), conditions)
        elif rating_step_type == RatingStep.RatingStepType.LINEAR_INTERPOLATE:
            step = RatingStep.LinearInterpolate(data.target, params, RatingFactorRepository(rating_manual_id, self.db_session), conditions)
        else:
            step = None

        return step

    def create_rating_step_parameters(self, rating_step_parameters_data: List[RatingStepParameterModel]):
        params = []
        for row in rating_step_parameters_data:
            parameter_type = RatingStepParameterType(row.parameter_type)
            param = RatingStepParameter(row.label, row.value, parameter_type)
            params.append(param)
        return params

    def create_rating_step_conditions(self, conditions: str = None):
        if conditions is None:
            return None

        structured_conditions = json.loads(conditions)

        return self.parse_structured_conditions(structured_conditions)

    def parse_structured_conditions(self, structured_conditions):
        if type(structured_conditions) is dict:
            operator = list(structured_conditions.keys())[0]

            if operator in ['<', '<=', '>', '>=', '==', '!=', 'BETWEEN']:
                operands = self.parse_comparison_operator_params(structured_conditions[operator])
                return ComparisonOperation(operator, operands)

            elif operator in ['AND', 'OR', 'NOT']:
                operands = self.parse_structured_conditions(structured_conditions[operator])
                return LogicalOperation(operator, operands)

        elif type(structured_conditions) is list:
            new_list = []
            for condition in structured_conditions:
                new_list.append(self.parse_structured_conditions(condition))
            return new_list

    def parse_comparison_operator_params(self, params: List[dict]):
        returns = []
        for param in params:
            returns.append(RatingStepParameter(
                param['label'],
                param['value'],
                RatingStepParameterType.LITERAL if param['type'] == 'LITERAL' else RatingStepParameterType.VARIABLE
            ))
        return returns
