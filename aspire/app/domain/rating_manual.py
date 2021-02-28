from typing import List
from .rating_step import AbstractRatingStep
from .rating_variable import RatingVariable


class RatingManual(object):
    name: str
    description: str
    rating_steps: List[AbstractRatingStep] = []
    rating_variables: List[RatingVariable] = []

    def __init__(self, name, description, rating_steps: List[AbstractRatingStep],
                 rating_variables: List[RatingVariable]):
        self.name = name
        self.description = description
        self.rating_steps = rating_steps
        self.rating_variables = rating_variables

    def get_sub_risks(self):
        sub_risks = [rv.sub_risk_label for rv in self.rating_variables if rv.sub_risk_label]
        return list(set(sub_risks))

    def get_rating_variables_by_sub_risk(self):
        rating_variables = {None: []}

        for rating_variable in self.rating_variables:
            if rating_variable.sub_risk_label not in rating_variables.keys():
                rating_variables[rating_variable.sub_risk_label] = []
            rating_variables[rating_variable.sub_risk_label].append(rating_variable)
        return rating_variables
