import json
from .RatingManualRepository import RatingManualRepository
from database.models import RatingFactor as RatingFactorModel
from repo.RatingFactorRepository import RatingFactorRepository
from database.engine import setup_test_db_session


def test_parsing_rating_step_conditions():
    repo = RatingManualRepository(None)

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

    repository = RatingFactorRepository(1, session)
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

    repository = RatingFactorRepository(1, session)
    result = repository.lookup('test', {'num_col_1': 15}, {'step_up': 'num_col_1'})
    assert result == '0.50'

    result = repository.lookup('test', {'num_col_1': 15}, {'step_down': 'num_col_1'})
    assert result == '0.25'
