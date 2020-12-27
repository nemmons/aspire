import json
from aspire.app.database.models import RatingFactor as RatingFactorModel, \
    RatingManual as RatingManualModel, \
    RatingStep as RatingStepModel, \
    RatingStepParameter as RatingStepParameterModel
from aspire.app.repo import RatingFactorRepository, RatingManualRepository
from aspire.app.database.engine import setup_test_db_session
from aspire.app.domain.RatingStep import RatingStepType
from aspire.app.domain.RatingStepCondition import ComparisonOperation
from aspire.app.domain.RatingStepParameter import RatingStepParameterType


def test_parsing_rating_step_conditions():
    repo = RatingManualRepository.RatingManualRepository(None)

    sample1 = json.dumps({'<': [
        {'label': 'x', 'value': 'x', 'type': 'VARIABLE'},
        {'label': '1', 'value': '1', 'type': 'LITERAL'},
    ]})
    result1 = repo.parse_structured_conditions(json.loads(sample1))
    assert str(result1) == '(x < 1)'

    sample2 = json.dumps({
        'AND': [
            {'<': [
                {'label': 'x', 'value': 'x', 'type': 'VARIABLE'},
                {'label': '1', 'value': '1', 'type': 'LITERAL'},
            ]},
            {'>': [
                {'label': 'y', 'value': 'x', 'type': 'VARIABLE'},
                {'label': '1', 'value': '1', 'type': 'LITERAL'},
            ]},
        ]
    })
    result2 = repo.parse_structured_conditions(json.loads(sample2))
    assert str(result2) == '((x < 1) AND (y > 1))'

    sample3 = json.dumps({
        'AND': [
            {'<': [
                {'label': 'x', 'value': 'x', 'type': 'VARIABLE'},
                {'label': '1', 'value': '1', 'type': 'LITERAL'},
            ]},
            {'OR': [
                {'>': [
                    {'label': 'y', 'value': 'x', 'type': 'VARIABLE'},
                    {'label': '1', 'value': '1', 'type': 'LITERAL'},
                ]},
                {'==': [
                    {'label': 'z', 'value': 'x', 'type': 'VARIABLE'},
                    {'label': '1', 'value': '1', 'type': 'LITERAL'},
                ]}
            ]},
        ]
    })
    result3 = repo.parse_structured_conditions(json.loads(sample3))
    assert str(result3) == '((x < 1) AND ((y > 1) OR (z == 1)))'


def test_basic_rating_factor_repository_lookup():
    session = setup_test_db_session()

    session.add_all([
        RatingFactorModel(rating_manual_id=1, type='test', num_col_1=1, value='0.25'),
        RatingFactorModel(rating_manual_id=1, type='test', num_col_1=2, value='0.50'),
        RatingFactorModel(rating_manual_id=1, type='test', num_col_1=3, value='0.75'),
        RatingFactorModel(rating_manual_id=1, type='other_test', num_col_1=2, value='0.66'),
        RatingFactorModel(rating_manual_id=2, type='test', num_col_1=2, value='0.77')
    ])
    session.commit()

    repository = RatingFactorRepository.RatingFactorRepository(1, session)
    result = repository.lookup('test', {'num_col_1': 2})
    assert result == '0.50'


def test_rating_factor_repository_stepping():
    session = setup_test_db_session()

    session.add_all([
        RatingFactorModel(rating_manual_id=1, type='test', num_col_1=10, value='0.25'),
        RatingFactorModel(rating_manual_id=1, type='test', num_col_1=20, value='0.50'),
        RatingFactorModel(rating_manual_id=1, type='test', num_col_1=30, value='0.75'),
    ])
    session.commit()

    repository = RatingFactorRepository.RatingFactorRepository(1, session)
    result = repository.lookup('test', {'num_col_1': 15}, {'step_up': 'num_col_1'})
    assert result == '0.50'

    result = repository.lookup('test', {'num_col_1': 15}, {'step_down': 'num_col_1'})
    assert result == '0.25'


def test_rating_manual_repository_factory_rating_steps():
    def create_manual_with_one_rating_step(db_session, rating_step_type_id) -> RatingManualModel:
        manual = RatingManualModel(name='Test Manual')
        manual.rating_steps = [
            RatingStepModel(
                rating_step_type_id=rating_step_type_id,
                name='Set Base Rate',
                target='base_rate',
                rating_step_parameters=[
                    RatingStepParameterModel(
                        label='Test Filler Param 1',
                        value='Test Filler Param 1',
                        parameter_type=RatingStepParameterType.LITERAL
                    ),
                    RatingStepParameterModel(
                        label='Test Filler Param 2',
                        value='Test Filler Param 2',
                        parameter_type=RatingStepParameterType.LITERAL
                    ),
                ]
            ),
        ]
        db_session.add(manual)
        db_session.commit()

        return manual

    for rating_step_type in RatingStepType:
        session = setup_test_db_session()
        rating_manual_model = create_manual_with_one_rating_step(session, int(rating_step_type))

        repository = RatingManualRepository.RatingManualRepository(session)
        rating_manual = repository.get(rating_manual_model.id)
        assert rating_manual is not None
        assert len(rating_manual.rating_steps) == 1
        rating_step = rating_manual.rating_steps[0]
        assert rating_step.target == 'base_rate'
        assert rating_step.__class__.__name__.lower() == str(rating_step_type.name).lower().replace('_', '')


def test_rating_manual_repository_parse_loaded_conditions():
    session = setup_test_db_session()
    manual_model = RatingManualModel(name='Test Manual')
    manual_model.rating_steps = [
        RatingStepModel(
            rating_step_type_id=RatingStepType.SET,
            name='Test',
            target='base_rate',
            rating_step_parameters=[
                RatingStepParameterModel(
                    label='Test Filler Param 1',
                    value='Test Filler Param 1',
                    parameter_type=RatingStepParameterType.LITERAL
                ),
                RatingStepParameterModel(
                    label='Test Filler Param 2',
                    value='Test Filler Param 2',
                    parameter_type=RatingStepParameterType.LITERAL
                ),
            ],
            conditions='{">": [{"label":"x", "value":"x", "type":"VARIABLE"},'
                       '{"label":"5", "value":"5", "type":"LITERAL"}]}'
        ),
    ]
    session.add(manual_model)
    session.commit()

    repository = RatingManualRepository.RatingManualRepository(session)
    rating_manual = repository.get(manual_model.id)
    rating_step = rating_manual.rating_steps[0]
    rating_step_condition = rating_step.conditions
    assert type(rating_step_condition) == ComparisonOperation
    assert rating_step_condition.operator == '>'