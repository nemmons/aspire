from .RatingManual import RatingManual
from .RatingStep import Loop, AbstractRatingStep
import copy
from typing import List


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
                'rating_variables': copy.deepcopy(rating_variables)
            }]

        # apply each rating step sequentially to the rate inputs
        rating_variables = self.run_steps(self.rating_manual.rating_steps, rating_variables, capture_details)

        self.rating_variables = rating_variables
        return rating_variables['rate']

    def run_steps(self, rating_steps, rating_variables, capture_details):
        for rating_step in rating_steps:
            if isinstance(rating_step, Loop):
                rating_variables = self.handle_rate_loop(rating_step, rating_variables, capture_details)
            else:
                rating_variables = copy.copy(rating_step).run(rating_variables)

            if capture_details:
                self.detailed_results.append({
                    'step': copy.copy(rating_step),
                    'rating_variables': copy.deepcopy(rating_variables)
                })
        return rating_variables

    def handle_rate_loop(self, rating_step: Loop, rating_variables: dict, capture_details):
        sub_risk_label = rating_step.sub_risk_label.evaluate(rating_variables)
        sub_risks = rating_variables[sub_risk_label]  # type: List[dict]
        original_rating_variables = rating_variables.keys()
        for i, sub_risk_vars in enumerate(sub_risks):
            rating_variables = self.run_steps(rating_step.rating_steps, {**sub_risk_vars, **rating_variables}, capture_details)
            updated_sub_risk_vars = {k: rating_variables[k] for k in rating_variables.keys() - original_rating_variables}
            rating_variables = {k: rating_variables[k] for k in original_rating_variables}
            rating_variables[sub_risk_label][i] = updated_sub_risk_vars
        return rating_variables

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
