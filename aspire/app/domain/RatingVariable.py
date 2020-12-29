import json


class RatingVariable(object):
    name: str
    description: str
    variable_type: str
    is_input: bool
    is_required: bool
    default: str

    def __init__(self, name, description, variable_type, is_input, is_required):
        self.name = name
        self.description = description
        self.variable_type = variable_type
        self.is_input = is_input
        self.is_required = is_required

    def __str__(self):
        return self.name + ' (' + self.description + ')'


class StringRatingVariable(RatingVariable):
    length: int
    default: str
    options: list

    def __init__(self, name, description, variable_type, is_input, is_required, default, constraints, length):
        super().__init__(name, description, variable_type, is_input, is_required)
        if length is not None:
            self.length = int(length)
        self.default = default

        options = json.loads(constraints)
        if isinstance(options, list):
            self.options = options
            if length is None:
                self.length = max(options, key=len)


class DecimalRatingVariable(RatingVariable):
    precision: int
    scale: int
    min: int
    max: int
    default: float

    def __init__(self, name, description, variable_type, is_input, is_required, default, constraints, length):
        super().__init__(name, description, variable_type, is_input, is_required)

        self.default = float(default)
        self.min, self.max = map(convert_to_float, constraints.split(','))
        self.precision, self.scale = map(convert_to_int, length.split(','))


class IntegerRatingVariable(RatingVariable):
    min: int
    max: int
    default: int

    def __init__(self, name, description, variable_type, is_input, is_required, default, constraints, length):
        super().__init__(name, description, variable_type, is_input, is_required)

        self.default = convert_to_int(default)
        self.min, self.max = map(convert_to_int, constraints.split(','))


class BoolRatingVariable(RatingVariable):

    def __init__(self, name, description, variable_type, is_input, is_required, default, constraints, length):
        super().__init__(name, description, variable_type, is_input, is_required)

        self.default = default


def convert_to_int(value):
    if value is not None and value != '':
        return int(value)
    return None


def convert_to_float(value):
    if value is not None and value != '':
        return float(value)
    return None
