import json
from abc import ABC, abstractmethod
from typing import List

from sqlalchemy.orm import aliased

from aspire.app.database.models import RatingManual as RatingManualModel, RatingStep as RatingStepModel, \
    RatingStepParameter as RatingStepParameterModel, RatingVariable as RatingVariableModel
from aspire.app.domain import rating_step, rating_variable
from aspire.app.domain.rating_manual import RatingManual
from aspire.app.domain.rating_step_condition import LogicalOperation, ComparisonOperation
from aspire.app.domain.rating_step_parameter import RatingStepParameter, RatingStepParameterType
from aspire.app.repository import rating_factor_repository


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
        rating_step_alias = aliased(RatingStepModel)

        manual = self.db_session.query(RatingManualModel). \
            filter(RatingManualModel.id == rating_manual_id). \
            outerjoin(RatingManualModel.rating_steps).\
            outerjoin(RatingStepModel.loop_rating_steps.of_type(rating_step_alias)).\
            outerjoin(RatingStepModel.rating_step_parameters).\
            outerjoin(RatingManualModel.rating_variables).\
            one()

        rating_steps = [self.factory_rating_step(rs, rating_manual_id) for rs in manual.rating_steps]
        rating_variables = [factory_rating_variable(rv) for rv in manual.rating_variables]

        rating_manual = RatingManual(manual.name, manual.description, rating_steps, rating_variables)
        return rating_manual

    def list(self):
        manuals = [{"id": row.id, "name": row.name, "description": row.description}
                   for row in self.db_session.query(RatingManualModel).all()]
        return manuals

    def store(self, rating_manual_id=None):
        pass

    def factory_rating_step(self, data: RatingStepModel, rating_manual_id: int):
        rating_step_type = rating_step.RatingStepType(data.rating_step_type_id)

        params = create_rating_step_parameters(data.rating_step_parameters)
        conditions = create_rating_step_conditions(data.conditions)

        if rating_step_type == rating_step.RatingStepType.SET:
            step = rating_step.Set(data.target, params, conditions)
        elif rating_step_type == rating_step.RatingStepType.ADD:
            step = rating_step.Add(data.target, params, conditions)
        elif rating_step_type == rating_step.RatingStepType.SUBTRACT:
            step = rating_step.Subtract(data.target, params, conditions)
        elif rating_step_type == rating_step.RatingStepType.MULTIPLY:
            step = rating_step.Multiply(data.target, params, conditions)
        elif rating_step_type == rating_step.RatingStepType.DIVIDE:
            step = rating_step.Divide(data.target, params, conditions)
        elif rating_step_type == rating_step.RatingStepType.ROUND:
            step = rating_step.Round(data.target, params, conditions)
        elif rating_step_type == rating_step.RatingStepType.LOOKUP:
            step = rating_step.Lookup(data.target, params,
                                      rating_factor_repository.RatingFactorRepository(rating_manual_id, self.db_session),
                                      conditions)
        elif rating_step_type == rating_step.RatingStepType.LINEAR_INTERPOLATE:
            step = rating_step.LinearInterpolate(data.target, params,
                                                 rating_factor_repository.RatingFactorRepository(rating_manual_id,
                                                                                                 self.db_session),
                                                 conditions)
        elif rating_step_type == rating_step.RatingStepType.LOOP:
            loop_rating_steps = [self.factory_rating_step(rs, rating_manual_id) for rs in data.loop_rating_steps]
            step = rating_step.Loop(params, loop_rating_steps, conditions)
        elif rating_step_type == rating_step.RatingStepType.SUB_RISK_SUM:
            step = rating_step.SubRiskSum(data.target, params, conditions)
        elif rating_step_type == rating_step.RatingStepType.SUB_RISK_PRODUCT:
            step = rating_step.SubRiskProduct(data.target, params, conditions)
        else:
            step = None

        if step is not None:
            step.label(data.name, data.description)

        return step


def factory_rating_variable(rating_variable_data: RatingVariableModel):
    mappings = {
        'boolean': rating_variable.BoolRatingVariable,
        'integer': rating_variable.IntegerRatingVariable,
        'decimal': rating_variable.DecimalRatingVariable,
        'string': rating_variable.StringRatingVariable,
    }

    if rating_variable_data.variable_type not in mappings.keys():
        return None

    return mappings[rating_variable_data.variable_type](
        name=rating_variable_data.name,
        description=rating_variable_data.description,
        variable_type=rating_variable_data.variable_type,
        sub_risk_label=rating_variable_data.sub_risk_label,
        is_input=rating_variable_data.is_input,
        is_required=rating_variable_data.is_required,
        default=rating_variable_data.default,
        constraints=rating_variable_data.constraints,
        length=rating_variable_data.length,
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
