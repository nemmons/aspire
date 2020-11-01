from .RatingStep import \
    RatingStepParameter, \
    RatingStepParameterType, \
    Add, \
    Set


def test_evaluate_literal():
    param = RatingStepParameter(5, RatingStepParameterType.LITERAL)

    result = param.evaluate({})
    assert result == 5


def test_evaluate_variable():
    param = RatingStepParameter('rate', RatingStepParameterType.VARIABLE)

    result = param.evaluate({'rate': 5})
    assert result == 5


def test_add_variables():
    rating_variables = {
        'rate_part_1': 5,
        'rate_part_2': 7,
    }

    add_step = Add(
        'rate',
        RatingStepParameter('rate_part_1', RatingStepParameterType.VARIABLE),
        RatingStepParameter('rate_part_2', RatingStepParameterType.VARIABLE),
    )

    result = add_step.apply(rating_variables)
    assert result['rate'] == 12.0


def test_add_variables_converts_string_to_float():
    rating_variables = {
        'rate_part_1': 5,
        'rate_part_2': "7.5",
    }

    add_step = Add(
        'rate',
        RatingStepParameter('rate_part_1', RatingStepParameterType.VARIABLE),
        RatingStepParameter('rate_part_2', RatingStepParameterType.VARIABLE),
    )

    result = add_step.apply(rating_variables)
    assert result['rate'] == 12.5


def test_add_variable_to_literal():
    rating_variables = {
        'rate': 10
    }

    add_step = Add(
        'rate',
        RatingStepParameter('rate', RatingStepParameterType.VARIABLE),
        RatingStepParameter(100, RatingStepParameterType.LITERAL),
    )

    result = add_step.apply(rating_variables)
    assert result['rate'] == 110.0


def test_add_variable_to_literal_string():
    rating_variables = {
        'rate': 10
    }

    add_step = Add(
        'rate',
        RatingStepParameter('rate', RatingStepParameterType.VARIABLE),
        RatingStepParameter("100", RatingStepParameterType.LITERAL),
    )

    result = add_step.apply(rating_variables)
    assert result['rate'] == 110.0


def test_set_variable_from_literal():
    rating_variables = {}

    set_step = Set(
        'rate',
        RatingStepParameter(100, RatingStepParameterType.LITERAL),
    )

    result = set_step.apply(rating_variables)
    assert result['rate'] == 100


def test_set_variable_from_variable():
    rating_variables = {
        'rate': 150
    }

    set_step = Set(
        'new_rate',
        RatingStepParameter('rate', RatingStepParameterType.VARIABLE),
    )

    result = set_step.apply(rating_variables)
    assert result['new_rate'] == 150
