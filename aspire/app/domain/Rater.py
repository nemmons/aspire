from .RatingManual import RatingManual
import copy


class Rater:
    rating_manual: RatingManual = None
    rating_variables: dict = None
    detailed_results: list = None

    def __init__(self, rating_manual: RatingManual):
        self.rating_manual = rating_manual

    def rate(self, rate_inputs, capture_details=False):
        rating_variables = rate_inputs

        if capture_details:
            self.detailed_results = [{
                'step': {'name': 'Initial Input'},
                'rating_variables': rating_variables.copy()
            }]

        # apply each rating step sequentially to the rate inputs
        for rating_step in self.rating_manual.rating_steps:
            rating_variables = rating_step.run(rating_variables)

            if capture_details:
                self.detailed_results.append({
                    'step': copy.copy(rating_step),
                    'rating_variables': rating_variables.copy()
                })

        self.rating_variables = rating_variables
        return rating_variables['rate']

    def check_output(self, rating_variable: str):
        if rating_variable in self.rating_variables:
            return self.rating_variables[rating_variable]
        return None

    def get_step_by_step_diff(self):
        diffed_results = [self.detailed_results[0]]
        for key, result in enumerate(self.detailed_results):
            if key == 0:
                continue

            prev_vars = self.detailed_results[key - 1]['rating_variables']
            current_vars = result['rating_variables']
            diffed_vars = {}

            for k in current_vars.keys():
                if k not in prev_vars or prev_vars[k] != current_vars[k]:
                    diffed_vars[k] = current_vars[k]

            diffed_results.append({
                'step': result['step'],
                'rating_variables': diffed_vars
            })

        return diffed_results
