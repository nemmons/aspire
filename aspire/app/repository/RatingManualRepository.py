import json
from abc import ABC, abstractmethod
from typing import List

from sqlalchemy.orm import joinedload

from aspire.app.database.models import RatingManual as RatingManualModel, RatingStep as RatingStepModel, \
    RatingStepParameter as RatingStepParameterModel, RatingVariable as RatingVariableModel
from aspire.app.domain import RatingManual, RatingStep, RatingVariable
from aspire.app.domain.RatingStepCondition import LogicalOperation, ComparisonOperation
from aspire.app.domain.RatingStepParameter import RatingStepParameter, RatingStepParameterType
from aspire.app.repository import RatingFactorRepository


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
            options(
            joinedload(RatingManualModel.rating_steps).joinedload(RatingStepModel.rating_step_parameters),
            joinedload(RatingManualModel.rating_variables)
        ).one()

        rating_steps = [self.factory_rating_step(rs, rating_manual_id) for rs in manual.rating_steps]
        rating_variables = [factory_rating_variable(rv) for rv in manual.rating_variables]

        rating_manual = RatingManual.RatingManual(manual.name, manual.description, rating_steps, rating_variables)
        return rating_manual

    def list(self):
        manuals = [{"id": row.id, "name": row.name, "description": row.description}
                   for row in self.db_session.query(RatingManualModel).all()]
        return manuals

    def store(self, rating_manual_id=None):
        pass

    def factory_rating_step(self, data: RatingStepModel, rating_manual_id: int):
        rating_step_type = RatingStep.RatingStepType(data.rating_step_type_id)

        params = create_rating_step_parameters(data.rating_step_parameters)
        conditions = create_rating_step_conditions(data.conditions)

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
            step = RatingStep.Lookup(data.target, params,
                                     RatingFactorRepository.RatingFactorRepository(rating_manual_id, self.db_session),
                                     conditions)
        elif rating_step_type == RatingStep.RatingStepType.LINEAR_INTERPOLATE:
            step = RatingStep.LinearInterpolate(data.target, params,
                                                RatingFactorRepository.RatingFactorRepository(rating_manual_id,
                                                                                              self.db_session),
                                                conditions)
        else:
            step = None

        if step is not None:
            step.label(data.name, data.description)

        return step


def factory_rating_variable(rating_variable: RatingVariableModel):
    mappings = {
        'boolean': RatingVariable.BoolRatingVariable,
        'integer': RatingVariable.IntegerRatingVariable,
        'decimal': RatingVariable.DecimalRatingVariable,
        'string': RatingVariable.StringRatingVariable,
    }

    if rating_variable.variable_type not in mappings.keys():
        return None

    return mappings[rating_variable.variable_type](
        name=rating_variable.name,
        description=rating_variable.description,
        variable_type=rating_variable.variable_type,
        is_input=rating_variable.is_input,
        is_required=rating_variable.is_required,
        default=rating_variable.default,
        constraints=rating_variable.constraints,
        length=rating_variable.length,
    )


def create_rating_step_parameters(rating_step_parameters_data: List[RatingStepParameterModel]):
    params = []
    for row in rating_step_parameters_data:
        parameter_type = RatingStepParameterType(row.parameter_type)
        param = RatingStepParameter(row.label, row.value, parameter_type)
        params.append(param)
    return params


def create_rating_step_conditions(conditions: str = None):
    if conditions is None:
        return None

    structured_conditions = json.loads(conditions)

    return parse_structured_conditions(structured_conditions)


def parse_structured_conditions(structured_conditions):
    if isinstance(structured_conditions, dict):
        operator = list(structured_conditions.keys())[0]

        if operator in ['<', '<=', '>', '>=', '==', '!=', 'BETWEEN']:
            operands = parse_comparison_operator_params(structured_conditions[operator])
            return ComparisonOperation(operator, operands)

        if operator in ['AND', 'OR', 'NOT']:
            operands = parse_structured_conditions(structured_conditions[operator])
            return LogicalOperation(operator, operands)

    elif isinstance(structured_conditions, list):
        new_list = []
        for condition in structured_conditions:
            new_list.append(parse_structured_conditions(condition))
        return new_list


def parse_comparison_operator_params(params: List[dict]):
    returns = []
    for param in params:
        returns.append(RatingStepParameter(
            param['label'],
            param['value'],
            RatingStepParameterType.LITERAL if param['type'] == 'LITERAL' else RatingStepParameterType.VARIABLE
        ))
    return returns
