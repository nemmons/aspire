from .RatingStep import Set, Add, Subtract, Multiply, Divide, Round, Lookup, LinearInterpolate

from .Rater import Rater

from .RatingManual import RatingManual

from .RatingStepParameter import \
    RatingStepParameter, \
    RatingStepParameterType

from .RatingVariable import \
    BoolRatingVariable, \
    DecimalRatingVariable, \
    IntegerRatingVariable, \
    StringRatingVariable

from aspire.app.repository.RatingFactorRepository import AbstractRatingFactorRepository
from aspire.app.repository.RatingManualRepository import AbstractRatingManualRepository

from . import Rater

from .RatingStepCondition import ComparisonOperation, LogicalOperation

from copy import deepcopy

import unittest


def test_evaluate_literal():
    param = RatingStepParameter('test', 5, RatingStepParameterType.LITERAL)

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


def test_subtract_rating_step():
    rating_variables = {
        'rate_part_1': 15,
        'rate_part_2': 7,
        'rate_part_3': 1,
    }

    add_step = Subtract(
        'rate',
        [
            RatingStepParameter('rate_part_1', 'rate_part_1', RatingStepParameterType.VARIABLE),
            RatingStepParameter('rate_part_2', 'rate_part_2', RatingStepParameterType.VARIABLE),
            RatingStepParameter('rate_part_3', 'rate_part_3', RatingStepParameterType.VARIABLE),
        ]
    )

    result = add_step.apply(rating_variables)
    assert result['rate'] == '7.0'


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


def test_divide_rating_step():
    rating_variables = {
        'rate_part_1': 35,
        'rate_part_2': 7,
        'rate_part_3': 2,
    }

    multiply_step = Divide(
        'rate',
        [
            RatingStepParameter('rate_part_1', 'rate_part_1', RatingStepParameterType.VARIABLE),
            RatingStepParameter('rate_part_2', 'rate_part_2', RatingStepParameterType.VARIABLE),
            RatingStepParameter('rate_part_3', 'rate_part_3', RatingStepParameterType.VARIABLE),
        ]
    )

    result = multiply_step.apply(rating_variables)
    assert result['rate'] == '2.5'


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


class MockRatingFactorRepository(AbstractRatingFactorRepository):
    def __init__(self):
        super().__init__()

    def lookup(self, rating_factor_type: str, params: dict, options: dict = None):
        if rating_factor_type == 'multiply_test':
            return params['base_rate_1'] * params['base_rate_2']
        if rating_factor_type == 'add_test':
            return params['base_rate_1'] + params['base_rate_2']
        return params['coverage'] * 5

    def get_factor(self, rating_factor_type: str, params: dict, options=None):
        pass


def test_lookup_step():
    repo = MockRatingFactorRepository()
    rating_variables = {}

    lookup_step = Lookup(
        'multiply_test',
        [
            RatingStepParameter('factor_type', 'multiply_test', RatingStepParameterType.LITERAL),
            RatingStepParameter('base_rate_1', 10, RatingStepParameterType.LITERAL),
            RatingStepParameter('base_rate_2', 15, RatingStepParameterType.LITERAL),
        ],
        repo
    )

    rating_variables = lookup_step.apply(rating_variables)
    assert rating_variables['multiply_test'] == 150

    lookup_step = Lookup(
        'add_test',
        [
            RatingStepParameter('factor_type', 'add_test', RatingStepParameterType.LITERAL),
            RatingStepParameter('base_rate_1', 10, RatingStepParameterType.LITERAL),
            RatingStepParameter('base_rate_2', 15, RatingStepParameterType.LITERAL),
        ],
        repo
    )

    rating_variables = lookup_step.apply(rating_variables)
    assert rating_variables['add_test'] == 25


def test_rater_e2e():
    class MockRatingManualRepository(AbstractRatingManualRepository):
        def __init__(self):
            super().__init__()

        def get(self, rating_manual_id=None):
            lookup_repo = MockRatingFactorRepository()

            rating_steps = [
                Lookup(
                    'base_rate',
                    [
                        RatingStepParameter('factor_type', 'base_rate', RatingStepParameterType.LITERAL),
                        RatingStepParameter('coverage', 'coverage', RatingStepParameterType.VARIABLE),
                    ],
                    lookup_repo
                ),
                Set(
                    'surcharge',
                    [RatingStepParameter('surcharge_amt', 450, RatingStepParameterType.LITERAL),]
                ),
                Add(
                    'rate',
                    [
                        RatingStepParameter('base_rate', 'base_rate', RatingStepParameterType.VARIABLE),
                        RatingStepParameter('surcharge', 'surcharge', RatingStepParameterType.VARIABLE),
                    ]
                ),
            ]
            return RatingManual("test", "test", rating_steps, [])

        def store(self, rating_manual_id=None):
            pass

    manual_repo = MockRatingManualRepository()
    manual = manual_repo.get()
    rater = Rater.Rater(manual)
    result = rater.rate({'coverage': 50})
    assert result == '700.0'


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


def test_rater_output():
    rating_steps = [
        Set(
            'some_value',
            [RatingStepParameter('test', 50, RatingStepParameterType.LITERAL)]
        ),
        Set(
            'rate',
            [RatingStepParameter('test', 100, RatingStepParameterType.LITERAL)]
        )
    ]
    rating_manual = RatingManual('Test Rating Manual', 'for testing', rating_steps, [])
    rater = Rater.Rater(rating_manual)

    rate = rater.rate({})
    assert rate == '100'
    assert rater.check_output('some_value') == '50'
    assert rater.check_output('nothing') is None


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


def test_lookup_step_options():
    class MockFactorRepo(AbstractRatingFactorRepository):
        def __init__(self):
            super().__init__()

        def lookup(self, rating_factor_type: str, params: dict, options: dict = None):
            if 'x' in options and options['x'] == 'yes':
                return '1'
            return '0'

        def get_factor(self, rating_factor_type: str, params: dict, options=None):
            pass

    lookup_step = Lookup(
        'test',
        [
            RatingStepParameter('rating_factor_type', 'whatever', RatingStepParameterType.LITERAL),
            RatingStepParameter('options', 'x:yes', RatingStepParameterType.LITERAL),
        ],
        MockFactorRepo()
    )

    output = lookup_step.run({})
    assert 'test' in output and output['test'] == '1'


def test_linear_interpolate_step():
    class FakeRatingFactor(object):
        def __init__(self, x, value):
            self.x = x
            self.value = value

    class MockFactorRepo(AbstractRatingFactorRepository):
        def __init__(self):
            super().__init__()

        def lookup(self, rating_factor_type: str, params: dict, options: dict = None):
            pass

        def get_factor(self, rating_factor_type: str, params: dict, options=None):
            if 'step_down' in options:
                return FakeRatingFactor(5, 25)
            if 'step_up' in options:
                return FakeRatingFactor(10, 40)
            raise Exception("Bad Test Input")

    linear_interpolate_step = LinearInterpolate(
        'result',
        [
            RatingStepParameter('rating_factor_type', 'whatever', RatingStepParameterType.LITERAL),
            RatingStepParameter('options', 'interpolate:x', RatingStepParameterType.LITERAL),
            RatingStepParameter('x', 'x', RatingStepParameterType.VARIABLE),
        ],
        MockFactorRepo()
    )
    linear_interpolate_step2 = deepcopy(linear_interpolate_step)  # running the step is destructive to the params
    linear_interpolate_step3 = deepcopy(linear_interpolate_step)

    output = linear_interpolate_step.run({'x': 7})
    assert output['result'] == '31.0'

    output = linear_interpolate_step2.run({'x': 5})
    assert output['result'] == '25.0'

    output = linear_interpolate_step3.run({'x': 10})
    assert output['result'] == '40.0'

    class MissingInterpolateValue(unittest.TestCase):
        def test(self):
            step = LinearInterpolate(
                'result',
                [
                    RatingStepParameter('rating_factor_type', 'whatever', RatingStepParameterType.LITERAL),
                    RatingStepParameter('options', 'interpolate:y', RatingStepParameterType.LITERAL),
                    RatingStepParameter('x', 'x', RatingStepParameterType.VARIABLE),
                ],
                MockFactorRepo()
            )
            with self.assertRaises(Exception):
                step.run({'x': 5})

    test = MissingInterpolateValue()
    test.test()


def test_string_rating_variable():
    import json
    options = ['masonry', 'masonry veneer', 'frame']
    var = StringRatingVariable(
        'Construction Type',
        'The type of construction',
        'string',
        True,
        True,
        'masonry',
        json.dumps(options),
        14
    )
    assert var.options == options


def test_decimal_rating_variable():
    var = DecimalRatingVariable(
        'Some decimal thing',
        'test',
        'decimal',
        True,
        True,
        '2.50',
        '1.25,7.25',
        '3,2'
    )
    assert var.min == 1.25
    assert var.max == 7.25
    assert var.precision == 3
    assert var.scale == 2


def test_integer_rating_variable():
    var = IntegerRatingVariable(
        'Age of Home',
        'The number of years since the house has been built',
        'integer',
        True,
        True,
        '15',
        '0,250',
        None
    )
    assert var.min == 0
    assert var.max == 250

    var = IntegerRatingVariable(
        'Amount of Insurance',
        'The amount of insurance...',
        'integer',
        True,
        True,
        None,
        '100000,',
        None
    )
    assert var.min == 100000
    assert var.max is None
