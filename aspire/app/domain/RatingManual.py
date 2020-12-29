from typing import List
from .RatingStep import AbstractRatingStep
from .RatingVariable import RatingVariable


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
