from abc import ABC, abstractmethod
from sqlalchemy import asc, desc
from sqlalchemy.orm import session
from aspire.app.database.models import RatingFactor as RatingFactorModel, get_custom_rating_factors_model


class AbstractRatingFactorRepository(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def lookup(self, rating_factor_type: str, params: dict, options=None):
        pass

    @abstractmethod
    def get_factor(self, rating_factor_type: str, params: dict, options=None):
        pass


class RatingFactorRepository(AbstractRatingFactorRepository):
    def __init__(self, rating_manual_id, db_session: session):
        super().__init__()
        self.rating_manual_id = rating_manual_id
        self.db_session = db_session

    def lookup(self, rating_factor_type: str, params: dict, options: dict = None):
        result = self.get_factor(rating_factor_type, params, options)
        return result.value

    def get_factor(self, rating_factor_type: str, params: dict, options: dict = None):
        options = {} if not options else options

        if "table" in options.keys():
            custom_model = True
            rating_factor_model = get_custom_rating_factors_model(options['table'], self.db_session.get_bind())
        else:
            custom_model = False
            rating_factor_model = RatingFactorModel

        query = self.db_session.query(rating_factor_model)

        if not custom_model:
            query = query \
                .filter(rating_factor_model.rating_manual_id == self.rating_manual_id) \
                .filter(rating_factor_model.type == rating_factor_type)

        if "step_up" in options.keys():
            col_to_step = options['step_up']
            target = params[col_to_step]
            params.pop(col_to_step)

            query = query.filter(getattr(rating_factor_model, col_to_step) >= target) \
                .order_by(asc(col_to_step))
        elif "step_down" in options.keys():
            col_to_step = options['step_down']
            target = params[col_to_step]
            params.pop(col_to_step)

            query = query.filter(getattr(rating_factor_model, col_to_step) <= target) \
                .order_by(desc(col_to_step))

        result = query.filter_by(**params).first()
        return result  # Todo hydrate into something other than a RatingFactorModel - this should be a domain entity
