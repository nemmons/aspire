from typing import List
from .RatingStep import AbstractRatingStep


class RatingManual(object):
    name: str
    description: str
    rating_steps: List[AbstractRatingStep] = []

    def __init__(self, name, description, rating_steps: List[AbstractRatingStep]):
        self.name = name
        self.description = description
        self.rating_steps = rating_steps
