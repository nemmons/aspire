from flask_rater.domain.Rater import Rater


def rate(rating_manual_id, rating_manual_repository, rating_inputs):
    rating_manual = rating_manual_repository.get(rating_manual_id)

    rater = Rater(rating_manual)
    rate_result = rater.rate(rating_inputs)

    return rate_result
