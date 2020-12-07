from .RatingStep import \
    Add, \
    Set, \
    Multiply, \
    Round

from .RatingStepParameter import \
    RatingStepParameter, \
    RatingStepParameterType


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
