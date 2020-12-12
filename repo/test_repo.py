import json
from .RatingManualRepository import RatingManualRepository


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
