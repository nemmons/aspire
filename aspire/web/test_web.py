import pytest

from . import create_webapp
from aspire.app.database.engine import setup_test_db_session

from aspire.app.domain.rating_step import RatingStepType
from aspire.app.domain.rating_step_parameter import RatingStepParameterType
from aspire.app.database.models import RatingManual, RatingStep, RatingVariable, RatingStepParameter


@pytest.fixture
def setup():
    session = setup_test_db_session()
    app = create_webapp({
        'TESTING': True,
        'SECRET_KEY': 'abc123',
        'session': session
    })

    with app.test_client() as client:
        yield client, session


def test_populated_rating_manuals_index(setup):
    client, session = setup

    manuals = [
        RatingManual(name="Test Homeowners Rating Manual", description="Insurance for Homeowners"),
        RatingManual(name="Test Auto Rating Manual", description="Insurance for Drivers")
    ]
    session.add_all(manuals)
    session.commit()

    response = client.get('/rating-manuals/')

    for manual in manuals:
        assert bytes("#" + str(manual.id), 'UTF-8') in response.data
        assert bytes(manual.name, 'UTF-8') in response.data
        assert bytes(manual.description, 'UTF-8') in response.data


def test_empty_rating_manuals_index(setup):
    client, _ = setup
    response = client.get('/rating-manuals/')
    assert b'No Rating Manuals found!' in response.data


def test_rating_manual_display(setup):
    client, session = setup
    rating_steps = [
        RatingStep(
            name="Set Base Rate",
            description="Initialize a base rate",
            target="base_rate",
            rating_step_type_id=int(RatingStepType.SET),
            rating_step_parameters=[
                RatingStepParameter(
                    parameter_type=int(RatingStepParameterType.LITERAL),
                    label="base_rate",
                    value="50.00"
                )
            ]
        ),
        RatingStep(
            name="Calculate Risk premium",
            description="Derive premium from square footage",
            target="risk_premium",
            rating_step_type_id=int(RatingStepType.MULTIPLY),
            rating_step_parameters=[
                RatingStepParameter(
                    parameter_type=int(RatingStepParameterType.LITERAL),
                    label="square footage factor",
                    value="100.00"
                ),
                RatingStepParameter(
                    parameter_type=int(RatingStepParameterType.VARIABLE),
                    label="square footage",
                    value="square_footage"
                )
            ]
        ),
        RatingStep(
            name="Calculate Total Premium",
            description="Add the base rate to the risk premium",
            target="rate",
            rating_step_type_id=int(RatingStepType.ADD),
            rating_step_parameters=[
                RatingStepParameter(
                    parameter_type=int(RatingStepParameterType.VARIABLE),
                    label="base rate",
                    value="base_rate"
                ),
                RatingStepParameter(
                    parameter_type=int(RatingStepParameterType.VARIABLE),
                    label="risk premium",
                    value="risk_premium"
                )
            ]
        )
    ]
    rating_variables = [
        RatingVariable(
            name="square_footage",
            description="the total liveable square footage of the risk",
            variable_type="integer",
            is_input=True,
            is_required=True,
            constraints='0,5000',
        ),
    ]
    manual = RatingManual(
        name="Test Homeowners Rating Manual",
        description="Insurance for Homeowners",
    )
    manual.rating_steps = rating_steps
    manual.rating_variables = rating_variables

    session.add(manual)
    session.commit()

    response = client.get('/rating-manuals/' + str(manual.id))

    title = "Rating Manual #" + str(manual.id) + ": " + manual.name

    assert bytes(title, 'UTF-8') in response.data


def test_demo_seeding(setup):
    client, session = setup
    response = client.get('/demo/seed-data')
    assert response.status_code == 302
    response = client.get('/rating-manuals/')
    print(str(response.data))
    assert b"Demo HO Manual" in response.data
    assert b"Demo Auto Manual" in response.data
