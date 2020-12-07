from .RatingStep import \
    Add, \
    Set, \
    Multiply, \
    Round

from .RatingStepParameter import \
    RatingStepParameter, \
    RatingStepParameterType

from .RatingStepCondition import ComparisonOperation, LogicalOperation


def test_evaluate_literal():
    param = RatingStepParameter('test', 5, RatingStepParameterType.LITERAL)
    assert str(param) == 'test'

    result = param.evaluate({})
    assert result == 5


def test_evaluate_variable():
    param = RatingStepParameter('rate', 'rate', RatingStepParameterType.VARIABLE)

    result = param.evaluate({'rate': 5})
    assert result == 5


def test_add_rating_step():
    rating_variables = {
        'rate_part_1': 5,
        'rate_part_2': 7,
    }

    add_step = Add(
        'rate',
        [
            RatingStepParameter('rate_part_1', 'rate_part_1', RatingStepParameterType.VARIABLE),
            RatingStepParameter('rate_part_2', 'rate_part_2', RatingStepParameterType.VARIABLE),
        ]
    )

    result = add_step.apply(rating_variables)
    assert result['rate'] == '12.0'


def test_multiply_rating_step():
    rating_variables = {
        'rate_part_1': 5,
        'rate_part_2': 7,
    }

    multiply_step = Multiply(
        'rate',
        [
            RatingStepParameter('rate_part_1', 'rate_part_1', RatingStepParameterType.VARIABLE),
            RatingStepParameter('rate_part_2', 'rate_part_2', RatingStepParameterType.VARIABLE),
        ]
    )

    result = multiply_step.apply(rating_variables)
    assert result['rate'] == '35.0'


def test_round_rating_step():
    rating_variables = {
        'value': 5.36491,
    }

    round_step = Round(
        'result',
        [
            RatingStepParameter('value', 'value', RatingStepParameterType.VARIABLE),
            RatingStepParameter('places', 2, RatingStepParameterType.LITERAL),
        ]
    )

    result = round_step.apply(rating_variables)
    assert result['result'] == '5.36'

    round_step = Round(
        'result',
        [
            RatingStepParameter('value', 'value', RatingStepParameterType.VARIABLE),
            RatingStepParameter('places', 3, RatingStepParameterType.LITERAL),
        ]
    )

    result = round_step.apply(rating_variables)
    assert result['result'] == '5.365'


def test_add_variables_converts_string_to_float():
    rating_variables = {
        'rate_part_1': 5,
        'rate_part_2': "7.5",
    }

    add_step = Add(
        'rate',
        [
            RatingStepParameter('rate_part_1', 'rate_part_1', RatingStepParameterType.VARIABLE),
            RatingStepParameter('rate_part_2', 'rate_part_2', RatingStepParameterType.VARIABLE),
        ]
    )

    result = add_step.apply(rating_variables)
    assert result['rate'] == '12.5'


def test_add_variable_to_literal():
    rating_variables = {
        'rate': 10
    }

    add_step = Add(
        'rate',
        [
            RatingStepParameter('rate', 'rate', RatingStepParameterType.VARIABLE),
            RatingStepParameter('surcharge', 100, RatingStepParameterType.LITERAL),
        ]
    )

    result = add_step.apply(rating_variables)
    assert result['rate'] == '110.0'


def test_add_variable_to_literal_string():
    rating_variables = {
        'rate': 10
    }

    add_step = Add(
        'rate',
        [
            RatingStepParameter('rate', 'rate', RatingStepParameterType.VARIABLE),
            RatingStepParameter('surcharge', "100", RatingStepParameterType.LITERAL),
        ]
    )

    result = add_step.apply(rating_variables)
    assert result['rate'] == '110.0'


def test_set_rating_step():
    rating_variables = {}

    set_step = Set(
        'rate',
        [RatingStepParameter('test', 100, RatingStepParameterType.LITERAL)]
    )

    result = set_step.apply(rating_variables)
    assert result['rate'] == '100'


def test_set_rating_step_from_variable():
    rating_variables = {
        'rate': 150
    }

    set_step = Set(
        'new_rate',
        [RatingStepParameter('rate', 'rate', RatingStepParameterType.VARIABLE)]
    )

    result = set_step.apply(rating_variables)
    assert result['new_rate'] == '150'


def test_binary_operator_comparisons():
    test_cases = [
        ['<', 5, 4, True],
        ['<', 5, 5, False],
        ['<', 5, 6, False],
        ['<=', 5, 4, True],
        ['<=', 5, 5, True],
        ['<=', 5, 6, False],
        ['>', 5, 4, False],
        ['>', 5, 5, False],
        ['>', 5, 6, True],
        ['>=', 5, 4, False],
        ['>=', 5, 5, True],
        ['>=', 5, 6, True],
        ['==', 5, 5, True],
        ['==', 5, 4, False],
        ['!=', 5, 5, False],
        ['!=', 5, 4, True]
    ]
    for test_case in test_cases:
        operation = test_case[0]
        operand_2 = test_case[1]
        operand_1 = test_case[2]
        expectation = test_case[3]

        comparison = ComparisonOperation(operation, [
            RatingStepParameter('x', 'x', RatingStepParameterType.VARIABLE),
            RatingStepParameter('target', operand_2, RatingStepParameterType.LITERAL),
        ])
        assert comparison.check({'x': operand_1}) is expectation


def test_between_comparison():
    between_5_and_7_comparison = ComparisonOperation('BETWEEN', [
        RatingStepParameter('x', 'x', RatingStepParameterType.VARIABLE),
        RatingStepParameter('5', '5', RatingStepParameterType.LITERAL),
        RatingStepParameter('7', '7', RatingStepParameterType.LITERAL),
    ])

    assert between_5_and_7_comparison.check({'x': 4}) is False
    assert between_5_and_7_comparison.check({'x': 5}) is True
    assert between_5_and_7_comparison.check({'x': 6}) is True
    assert between_5_and_7_comparison.check({'x': 8}) is False


def test_logical_comparison_operations():
    less_than_6_comparison = ComparisonOperation('<', [
        RatingStepParameter('x', 'x', RatingStepParameterType.VARIABLE),
        RatingStepParameter('6', '6', RatingStepParameterType.LITERAL),
    ])
    between_5_and_7_comparison = ComparisonOperation('BETWEEN', [
        RatingStepParameter('x', 'x', RatingStepParameterType.VARIABLE),
        RatingStepParameter('5', '5', RatingStepParameterType.LITERAL),
        RatingStepParameter('7', '7', RatingStepParameterType.LITERAL),
    ])

    intersection_comparison = LogicalOperation('AND', [less_than_6_comparison, between_5_and_7_comparison])

    assert str(intersection_comparison) == '((x < 6) AND (x BETWEEN 5 AND 7))'

    assert intersection_comparison.check({'x': 5}) is True
    assert intersection_comparison.check({'x': 6}) is False
    assert intersection_comparison.check({'x': 7}) is False

    union_comparison = LogicalOperation('OR', [less_than_6_comparison, between_5_and_7_comparison])

    assert union_comparison.check({'x': 5}) is True
    assert union_comparison.check({'x': 6}) is True
    assert union_comparison.check({'x': 7}) is True
    assert union_comparison.check({'x': 8}) is False

    not_comparison = LogicalOperation('NOT', [less_than_6_comparison])

    assert not_comparison.check({'x': 5}) is False
    assert not_comparison.check({'x': 6}) is True
    assert not_comparison.check({'x': 7}) is True

    assert str(not_comparison) == '(NOT (x < 6))'


def test_bad_operations():
    bad_comparison = ComparisonOperation('???', [])
    assert bad_comparison.check({}) is False
    assert str(bad_comparison) == ''

    bad_logical = LogicalOperation('???', [])
    assert bad_logical.check({}) is False
    assert str(bad_logical) == ''


def test_rating_step_conditions():
    less_than_6_comparison = ComparisonOperation('<', [
        RatingStepParameter('x', 'x', RatingStepParameterType.VARIABLE),
        RatingStepParameter('6', '6', RatingStepParameterType.LITERAL),
    ])

    rating_step = Set(
        'rate',
        [RatingStepParameter('test', 100, RatingStepParameterType.LITERAL)],
        less_than_6_comparison
    )

    output = rating_step.run({'x': 5})
    assert output == {'x': 5, 'rate': '100'}

    output = rating_step.run({'x': 6})
    assert output == {'x': 6}
