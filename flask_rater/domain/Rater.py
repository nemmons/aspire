from .RatingManual import RatingManual


class Rater:
    rating_manual: RatingManual = None
    rating_variables: dict = None

    def __init__(self, rating_manual: RatingManual):
        self.rating_manual = rating_manual

    def rate(self, rate_inputs):
        rating_variables = rate_inputs

        # apply each rating step sequentially to the rate inputs
        for rating_step in self.rating_manual.rating_steps:
            rating_variables = rating_step.run(rating_variables)

        self.rating_variables = rating_variables
        return rating_variables['rate']

    def check_output(self, rating_variable: str):
        if rating_variable in self.rating_variables:
            return self.rating_variables[rating_variable]
        return None
