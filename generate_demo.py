from web import create_app
from database.models import RatingManual, RatingStep, RatingStepParameter, RatingFactor
from domain.RatingStep import RatingStepType as RatingStepTypeEnum
from domain.RatingStepParameter import RatingStepParameterType as RatingStepParameterTypeEnum

app = create_app()

db_session = app.session

rating_manual = RatingManual(
    name='Demo HO Manual',
    description='Example HO Manual from Chapter 2 of CAS \'Basic Ratemaking\' PDF ('
                'https://www.casact.org/library/studynotes/Werner_Modlin_Ratemaking.pdf) ',
)

rating_steps = [
    RatingStep(
        rating_step_type_id=int(RatingStepTypeEnum.SET),
        rating_step_parameters=[
            RatingStepParameter(
                parameter_order=1,
                label='Base Rate',
                value='500',
                parameter_type=int(RatingStepParameterTypeEnum.LITERAL)
            )
        ],
        name='Set Base Rate',
        description='The base rate is a constant $500',
        step_order=1,
        target='base_rate'
    ),
    RatingStep(
        rating_step_type_id=int(RatingStepTypeEnum.LINEAR_INTERPOLATE),
        rating_step_parameters=[
            RatingStepParameter(
                parameter_order=1,
                label='rating_factor_type',
                value='amount_of_insurance',
                parameter_type=int(RatingStepParameterTypeEnum.LITERAL)
            ),
            RatingStepParameter(
                parameter_order=2,
                label='options',
                value='interpolate:amount_of_insurance',
                parameter_type=int(RatingStepParameterTypeEnum.LITERAL)
            ),
            RatingStepParameter(
                parameter_order=3,
                label='num_col_1',
                value='amount_of_insurance',
                parameter_type=int(RatingStepParameterTypeEnum.VARIABLE)
            )
        ],
        name='Lookup Amount of Insurance Factor',
        description='Performs linear interpolation on values up to 500k from rating tables',
        step_order=2,
        target='amount_of_insurance_factor'
    ),
    RatingStep(
        rating_step_type_id=int(RatingStepTypeEnum.SUBTRACT),
        rating_step_parameters=[
            RatingStepParameter(
                parameter_order=1,
                label='amount_of_insurance',
                value='amount_of_insurance',
                parameter_type=int(RatingStepParameterTypeEnum.VARIABLE)
            ),
            RatingStepParameter(
                parameter_order=2,
                label='interpolation limit',
                value='500000',
                parameter_type=int(RatingStepParameterTypeEnum.LITERAL)
            )
        ],
        name='Calculate amount of insurance over 500k',
        description='Coverage up to 500k is interpolated; afterwards, every 15k adds .03 to the rating factor',
        step_order=3,
        target='insurance_over_500k',
        conditions='{">": [{"label":"amount_of_insurance", "value":"amount_of_insurance", "type":"VARIABLE"},'
                   '{"label":"500k", "value":"500000", "type":"LITERAL"}]}'
    ),
    RatingStep(
        rating_step_type_id=int(RatingStepTypeEnum.MULTIPLY),
        rating_step_parameters=[
            RatingStepParameter(
                parameter_order=1,
                label='insurance_over_500k',
                value='insurance_over_500k',
                parameter_type=int(RatingStepParameterTypeEnum.VARIABLE)
            ),
            RatingStepParameter(
                parameter_order=2,
                label='.03 / 15k',
                value='0.000002',
                parameter_type=int(RatingStepParameterTypeEnum.LITERAL)
            )
        ],
        name='Calculate amount of insurance over 500k FACTOR',
        description='Every 15k adds .03 to the rating factor',
        step_order=4,
        target='insurance_over_500k_factor',
        conditions='{">": [{"label":"amount_of_insurance", "value":"amount_of_insurance", "type":"VARIABLE"},'
                   '{"label":"500k", "value":"500000", "type":"LITERAL"}]}'
    ),
    RatingStep(
        rating_step_type_id=int(RatingStepTypeEnum.ADD),
        rating_step_parameters=[
            RatingStepParameter(
                parameter_order=1,
                label='amount_of_insurance_factor',
                value='amount_of_insurance_factor',
                parameter_type=int(RatingStepParameterTypeEnum.VARIABLE)
            ),
            RatingStepParameter(
                parameter_order=2,
                label='insurance_over_500k_factor',
                value='insurance_over_500k_factor',
                parameter_type=int(RatingStepParameterTypeEnum.VARIABLE)
            ),
        ],
        name='Calculate amount of insurance over 500k FACTOR',
        step_order=5,
        target='amount_of_insurance_factor',
        conditions='{">": [{"label":"amount_of_insurance", "value":"amount_of_insurance", "type":"VARIABLE"},'
                   '{"label":"500k", "value":"500000", "type":"LITERAL"}]}'
    ),
    RatingStep(
        rating_step_type_id=int(RatingStepTypeEnum.LOOKUP),
        rating_step_parameters=[
            RatingStepParameter(
                parameter_order=1,
                label='rating_factor_type',
                value='territory',
                parameter_type=int(RatingStepParameterTypeEnum.LITERAL)
            ),
            RatingStepParameter(
                parameter_order=2,
                label='num_col_1',
                value='territory',
                parameter_type=int(RatingStepParameterTypeEnum.VARIABLE)
            )
        ],
        name='Lookup Territory Factor',
        step_order=6,
        target='territory_factor'
    ),
    RatingStep(
        rating_step_type_id=int(RatingStepTypeEnum.LOOKUP),
        rating_step_parameters=[
            RatingStepParameter(
                parameter_order=1,
                label='rating_factor_type',
                value='prot_class_const_type',
                parameter_type=int(RatingStepParameterTypeEnum.LITERAL)
            ),
            RatingStepParameter(
                parameter_order=2,
                label='num_col_1',
                value='protection_class',
                parameter_type=int(RatingStepParameterTypeEnum.VARIABLE)
            ),
            RatingStepParameter(
                parameter_order=3,
                label='str_col_1',
                value='construction_type',
                parameter_type=int(RatingStepParameterTypeEnum.VARIABLE)
            )
        ],
        name='Lookup Protection Class/Construction Type Factor',
        step_order=7,
        target='prot_class_const_type_factor'
    ),
    RatingStep(
        rating_step_type_id=int(RatingStepTypeEnum.LOOKUP),
        rating_step_parameters=[
            RatingStepParameter(
                parameter_order=1,
                label='rating_factor_type',
                value='uw_tier',
                parameter_type=int(RatingStepParameterTypeEnum.LITERAL)
            ),
            RatingStepParameter(
                parameter_order=2,
                label='str_col_1',
                value='underwriting_tier',
                parameter_type=int(RatingStepParameterTypeEnum.VARIABLE)
            )
        ],
        name='Lookup Underwriting Tier Factor',
        step_order=8,
        target='uw_tier_factor'
    ),
    RatingStep(
        rating_step_type_id=int(RatingStepTypeEnum.LOOKUP),
        rating_step_parameters=[
            RatingStepParameter(
                parameter_order=1,
                label='rating_factor_type',
                value='deductible',
                parameter_type=int(RatingStepParameterTypeEnum.LITERAL)
            ),
            RatingStepParameter(
                parameter_order=2,
                label='num_col_1',
                value='deductible',
                parameter_type=int(RatingStepParameterTypeEnum.VARIABLE)
            )
        ],
        name='Lookup Deductible Factor',
        step_order=9,
        target='deductible_factor'
    ),
    RatingStep(
        rating_step_type_id=int(RatingStepTypeEnum.SET),
        rating_step_parameters=[
            RatingStepParameter(
                parameter_order=1,
                label='Default Factor',
                value='0',
                parameter_type=int(RatingStepParameterTypeEnum.LITERAL)
            )
        ],
        name='Set Default New Home Discount',
        step_order=10,
        target='new_home_discount'
    ),
    RatingStep(
        rating_step_type_id=int(RatingStepTypeEnum.SET),
        rating_step_parameters=[
            RatingStepParameter(
                parameter_order=1,
                label='Discount',
                value='-0.2',
                parameter_type=int(RatingStepParameterTypeEnum.LITERAL)
            )
        ],
        name='Set New Home Discount',
        step_order=11,
        target='new_home_discount',
        conditions='{"==": [{"label":"new_home", "value":"new_home", "type":"VARIABLE"},'
                   '{"label":"yes", "value":"yes", "type":"LITERAL"}]}'
    ),
    RatingStep(
        rating_step_type_id=int(RatingStepTypeEnum.SET),
        rating_step_parameters=[
            RatingStepParameter(
                parameter_order=1,
                label='Default Discount',
                value='0',
                parameter_type=int(RatingStepParameterTypeEnum.LITERAL)
            )
        ],
        name='Set Default 5-Year Claims Free Discount',
        step_order=12,
        target='five_year_claims_free_discount'
    ),
    RatingStep(
        rating_step_type_id=int(RatingStepTypeEnum.SET),
        rating_step_parameters=[
            RatingStepParameter(
                parameter_order=1,
                label='Discount',
                value='-0.1',
                parameter_type=int(RatingStepParameterTypeEnum.LITERAL)
            )
        ],
        name='Set 5-Year Claims Free Discount',
        step_order=13,
        target='five_year_claims_free_discount',
        conditions='{"==": [{"label":"five_years_claims_free", "value":"five_years_claims_free", "type":"VARIABLE"},'
                   '{"label":"yes", "value":"yes", "type":"LITERAL"}]}'
    ),
    RatingStep(
        rating_step_type_id=int(RatingStepTypeEnum.ADD),
        rating_step_parameters=[
            RatingStepParameter(
                parameter_order=1,
                label='Base',
                value='1',
                parameter_type=int(RatingStepParameterTypeEnum.LITERAL)
            ),
            RatingStepParameter(
                parameter_order=1,
                label='New Home Discount',
                value='new_home_discount',
                parameter_type=int(RatingStepParameterTypeEnum.VARIABLE)
            ),
            RatingStepParameter(
                parameter_order=2,
                label='Five Year Claims Free Discount',
                value='five_year_claims_free_discount',
                parameter_type=int(RatingStepParameterTypeEnum.VARIABLE)
            )
        ],
        name='Calculate New Home + Claims Free Discount Factor',
        step_order=14,
        target='new_home_claims_free_discount_factor',
    ),
    RatingStep(
        rating_step_type_id=int(RatingStepTypeEnum.SET),
        rating_step_parameters=[
            RatingStepParameter(
                parameter_order=1,
                label='Default Factor',
                value='1',
                parameter_type=int(RatingStepParameterTypeEnum.LITERAL)
            )
        ],
        name='Set Default Multi-Policy Discount Factor',
        step_order=15,
        target='multi_policy_discount_factor'
    ),
    RatingStep(
        rating_step_type_id=int(RatingStepTypeEnum.SET),
        rating_step_parameters=[
            RatingStepParameter(
                parameter_order=1,
                label='Default Factor',
                value='0.93',
                parameter_type=int(RatingStepParameterTypeEnum.LITERAL)
            )
        ],
        name='Set Multi-Policy Discount Factor',
        step_order=16,
        target='multi_policy_discount_factor',
        conditions='{"==": [{"label":"multi_policy", "value":"multi_policy", "type":"VARIABLE"},'
                   '{"label":"yes", "value":"yes", "type":"LITERAL"}]}'
    ),
    RatingStep(
        rating_step_type_id=int(RatingStepTypeEnum.LOOKUP),
        rating_step_parameters=[
            RatingStepParameter(
                parameter_order=1,
                label='rating_factor_type',
                value='jewelry_coverage',
                parameter_type=int(RatingStepParameterTypeEnum.LITERAL)
            ),
            RatingStepParameter(
                parameter_order=2,
                label='num_col_1',
                value='jewelry_coverage',
                parameter_type=int(RatingStepParameterTypeEnum.VARIABLE)
            )
        ],
        name='Lookup Jewelry Coverage Rate',
        step_order=17,
        target='jewelry_coverage_rate'
    ),
    RatingStep(
        rating_step_type_id=int(RatingStepTypeEnum.LOOKUP),
        rating_step_parameters=[
            RatingStepParameter(
                parameter_order=1,
                label='rating_factor_type',
                value='liability_medical_coverage',
                parameter_type=int(RatingStepParameterTypeEnum.LITERAL)
            ),
            RatingStepParameter(
                parameter_order=2,
                label='str_col_1',
                value='liability_medical_coverage',
                parameter_type=int(RatingStepParameterTypeEnum.VARIABLE)
            )
        ],
        name='Lookup Liability/Medical Coverage Rate',
        step_order=18,
        target='liability_medical_coverage_rate'
    ),
    RatingStep(
        rating_step_type_id=int(RatingStepTypeEnum.MULTIPLY),
        rating_step_parameters=[
            RatingStepParameter(
                parameter_order=1,
                label='Base Rate',
                value='base_rate',
                parameter_type=int(RatingStepParameterTypeEnum.VARIABLE)
            ),
            RatingStepParameter(
                parameter_order=2,
                label='Amount of Insurance Factor',
                value='amount_of_insurance_factor',
                parameter_type=int(RatingStepParameterTypeEnum.VARIABLE)
            ),
            RatingStepParameter(
                parameter_order=3,
                label='Territory Factor',
                value='territory_factor',
                parameter_type=int(RatingStepParameterTypeEnum.VARIABLE)
            ),
            RatingStepParameter(
                parameter_order=4,
                label='Protection Class/Construction Type Factor',
                value='prot_class_const_type_factor',
                parameter_type=int(RatingStepParameterTypeEnum.VARIABLE)
            ),
            RatingStepParameter(
                parameter_order=5,
                label='Underwriting Tier Factor',
                value='uw_tier_factor',
                parameter_type=int(RatingStepParameterTypeEnum.VARIABLE)
            ),
            RatingStepParameter(
                parameter_order=6,
                label='Deductible Factor',
                value='deductible_factor',
                parameter_type=int(RatingStepParameterTypeEnum.VARIABLE)
            ),
            RatingStepParameter(
                parameter_order=7,
                label='New Home + Claims Free Discount Factor',
                value='new_home_claims_free_discount_factor',
                parameter_type=int(RatingStepParameterTypeEnum.VARIABLE)
            ),
            RatingStepParameter(
                parameter_order=8,
                label='Multi-Policy Discount Factor',
                value='multi_policy_discount_factor',
                parameter_type=int(RatingStepParameterTypeEnum.VARIABLE)
            ),
        ],
        name='Calculate New Home + Claims Free Discount Factor',
        step_order=19,
        target='rate',
    ),
    RatingStep(
        rating_step_type_id=int(RatingStepTypeEnum.ROUND),
        rating_step_parameters=[
            RatingStepParameter(
                parameter_order=1,
                label='rate',
                value='rate',
                parameter_type=int(RatingStepParameterTypeEnum.VARIABLE)
            ),
            RatingStepParameter(
                parameter_order=2,
                label='Round to the Nearest Whole Dollar',
                value='0',
                parameter_type=int(RatingStepParameterTypeEnum.LITERAL)
            ),
        ],
        name='Round Rate',
        step_order=20,
        target='rate',
    ),
    RatingStep(
        rating_step_type_id=int(RatingStepTypeEnum.ADD),
        rating_step_parameters=[
            RatingStepParameter(
                parameter_order=1,
                label='Rate',
                value='rate',
                parameter_type=int(RatingStepParameterTypeEnum.VARIABLE)
            ),
            RatingStepParameter(
                parameter_order=1,
                label='Jewelry Coverage Rate',
                value='jewelry_coverage_rate',
                parameter_type=int(RatingStepParameterTypeEnum.VARIABLE)
            ),
            RatingStepParameter(
                parameter_order=2,
                label='Liability/Medical Coverage Rate',
                value='liability_medical_coverage_rate',
                parameter_type=int(RatingStepParameterTypeEnum.VARIABLE)
            )
        ],
        name='Add Other Coverage Rates',
        step_order=21,
        target='rate',
    ),
    RatingStep(
        rating_step_type_id=int(RatingStepTypeEnum.ADD),
        rating_step_parameters=[
            RatingStepParameter(
                parameter_order=1,
                label='Rate',
                value='rate',
                parameter_type=int(RatingStepParameterTypeEnum.VARIABLE)
            ),
            RatingStepParameter(
                parameter_order=1,
                label='Policy Fee',
                value='50',
                parameter_type=int(RatingStepParameterTypeEnum.LITERAL)
            ),
        ],
        name='Add Policy Fee',
        step_order=22,
        target='rate',
    ),
]

rating_factors = [
    RatingFactor(type='amount_of_insurance', num_col_1=80000, value='0.56'),
    RatingFactor(type='amount_of_insurance', num_col_1=95000, value='0.63'),
    RatingFactor(type='amount_of_insurance', num_col_1=110000, value='0.69'),
    RatingFactor(type='amount_of_insurance', num_col_1=125000, value='0.75'),
    RatingFactor(type='amount_of_insurance', num_col_1=140000, value='0.81'),
    RatingFactor(type='amount_of_insurance', num_col_1=155000, value='0.86'),
    RatingFactor(type='amount_of_insurance', num_col_1=170000, value='0.91'),
    RatingFactor(type='amount_of_insurance', num_col_1=185000, value='0.96'),
    RatingFactor(type='amount_of_insurance', num_col_1=200000, value='1'),
    RatingFactor(type='amount_of_insurance', num_col_1=215000, value='1.04'),
    RatingFactor(type='amount_of_insurance', num_col_1=230000, value='1.08'),
    RatingFactor(type='amount_of_insurance', num_col_1=245000, value='1.12'),
    RatingFactor(type='amount_of_insurance', num_col_1=260000, value='1.16'),
    RatingFactor(type='amount_of_insurance', num_col_1=275000, value='1.2'),
    RatingFactor(type='amount_of_insurance', num_col_1=290000, value='1.24'),
    RatingFactor(type='amount_of_insurance', num_col_1=305000, value='1.28'),
    RatingFactor(type='amount_of_insurance', num_col_1=320000, value='1.32'),
    RatingFactor(type='amount_of_insurance', num_col_1=335000, value='1.36'),
    RatingFactor(type='amount_of_insurance', num_col_1=350000, value='1.39'),
    RatingFactor(type='amount_of_insurance', num_col_1=365000, value='1.42'),
    RatingFactor(type='amount_of_insurance', num_col_1=380000, value='1.45'),
    RatingFactor(type='amount_of_insurance', num_col_1=395000, value='1.48'),
    RatingFactor(type='amount_of_insurance', num_col_1=410000, value='1.51'),
    RatingFactor(type='amount_of_insurance', num_col_1=425000, value='1.54'),
    RatingFactor(type='amount_of_insurance', num_col_1=440000, value='1.57'),
    RatingFactor(type='amount_of_insurance', num_col_1=455000, value='1.6'),
    RatingFactor(type='amount_of_insurance', num_col_1=470000, value='1.63'),
    RatingFactor(type='amount_of_insurance', num_col_1=485000, value='1.66'),
    RatingFactor(type='amount_of_insurance', num_col_1=500000, value='1.69'),
    RatingFactor(type='amount_of_insurance', num_col_1=50000000, value='1.69'),  # use the same factor for >=500k
    RatingFactor(type='territory', num_col_1=1, value='.80'),
    RatingFactor(type='territory', num_col_1=2, value='.90'),
    RatingFactor(type='territory', num_col_1=3, value='1.00'),
    RatingFactor(type='territory', num_col_1=4, value='1.10'),
    RatingFactor(type='territory', num_col_1=5, value='1.15'),
    RatingFactor(type='prot_class_const_type', num_col_1=5, value='1.15'),
    RatingFactor(type='prot_class_const_type', num_col_1=1, str_col_1='Frame', value='1'),
    RatingFactor(type='prot_class_const_type', num_col_1=2, str_col_1='Frame', value='1'),
    RatingFactor(type='prot_class_const_type', num_col_1=3, str_col_1='Frame', value='1'),
    RatingFactor(type='prot_class_const_type', num_col_1=4, str_col_1='Frame', value='1'),
    RatingFactor(type='prot_class_const_type', num_col_1=5, str_col_1='Frame', value='1.05'),
    RatingFactor(type='prot_class_const_type', num_col_1=6, str_col_1='Frame', value='1.1'),
    RatingFactor(type='prot_class_const_type', num_col_1=7, str_col_1='Frame', value='1.15'),
    RatingFactor(type='prot_class_const_type', num_col_1=8, str_col_1='Frame', value='1.25'),
    RatingFactor(type='prot_class_const_type', num_col_1=9, str_col_1='Frame', value='2.1'),
    RatingFactor(type='prot_class_const_type', num_col_1=10, str_col_1='Frame', value='2.3'),
    RatingFactor(type='prot_class_const_type', num_col_1=1, str_col_1='Masonry', value='0.9'),
    RatingFactor(type='prot_class_const_type', num_col_1=2, str_col_1='Masonry', value='0.9'),
    RatingFactor(type='prot_class_const_type', num_col_1=3, str_col_1='Masonry', value='0.9'),
    RatingFactor(type='prot_class_const_type', num_col_1=4, str_col_1='Masonry', value='0.9'),
    RatingFactor(type='prot_class_const_type', num_col_1=5, str_col_1='Masonry', value='1'),
    RatingFactor(type='prot_class_const_type', num_col_1=6, str_col_1='Masonry', value='1.05'),
    RatingFactor(type='prot_class_const_type', num_col_1=7, str_col_1='Masonry', value='1.1'),
    RatingFactor(type='prot_class_const_type', num_col_1=8, str_col_1='Masonry', value='1.15'),
    RatingFactor(type='prot_class_const_type', num_col_1=9, str_col_1='Masonry', value='1.75'),
    RatingFactor(type='prot_class_const_type', num_col_1=10, str_col_1='Masonry', value='1.9'),
    RatingFactor(type='uw_tier', str_col_1='A', value='.80'),
    RatingFactor(type='uw_tier', str_col_1='B', value='.95'),
    RatingFactor(type='uw_tier', str_col_1='C', value='1.00'),
    RatingFactor(type='uw_tier', str_col_1='D', value='1.45'),
    RatingFactor(type='deductible', num_col_1=250, value='1.00'),
    RatingFactor(type='deductible', num_col_1=500, value='.95'),
    RatingFactor(type='deductible', num_col_1=1000, value='.85'),
    RatingFactor(type='deductible', num_col_1=5000, value='.70'),
    RatingFactor(type='jewelry_coverage', num_col_1=2500, value='0'),
    RatingFactor(type='jewelry_coverage', num_col_1=5000, value='35'),
    RatingFactor(type='jewelry_coverage', num_col_1=10000, value='60'),
    RatingFactor(type='liability_medical_coverage', str_col_1='100000/500', value='0'),
    RatingFactor(type='liability_medical_coverage', str_col_1='300000/1000', value='25'),
    RatingFactor(type='liability_medical_coverage', str_col_1='500000/2500', value='45'),
]

rating_manual.rating_steps = rating_steps
rating_manual.rating_factors = rating_factors

db_session.add(rating_manual)
db_session.commit()
