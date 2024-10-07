import math
from enum import Enum
from typing import TypedDict, List
import pandas as pd
from importlib import resources as ir
from . import resources


class Model(Enum):
    MODEL_1 = "Basic Clinical Model"
    MODEL_2 = "Basic model with NT-proBNP"
    MODEL_3 = "Basic model with hs-cTnT"
    MODEL_4 = "Basic model with ST2"
    MODEL_5 = "Basic model with NT-proBNP and ST2"
    MODEL_6 = "Basic model with NT-proBNP and hs-cTnT"
    MODEL_7 = "Basic model with hs-cTNT and ST2"
    MODEL_8 = "Basic model with NT-proBNP + hs-cTNT + ST2"


Parameters = TypedDict('Parameters', {
    'Age (years)': int,
    'Female': bool,
    'NYHA Class': int,
    'Ejection fraction (%)': int,
    'Sodium (mmol/L)': int,
    'eGFR in mL/min/1.73m²': int,
    'Hemoglobin (g/dL)': float,
    'Loop Diuretic Furosemide Dose': int,
    'Statin': bool,
    'ACEi/ARB': bool,
    'Betablockers': bool,
    'NT-proBNP in pg/mL': int,
    'hs-cTnT in ng/L': float,
    'ST2 (ng/mL)': float,
})

MIN_MAX_MEDIAN = pd.DataFrame(
    {
        'lower_limit': [35, 10, 130, 6, 8.7, 21, 3, 18],
        'upper_limit': [88, 71, 147, 110, 17.1, 34800, 265, 157],
        'median_impute': [70.3, 34, 139, 42.4, 12.9, 1361.5, 22.6, 38.1]
    },
    index=['Age (years)', 'Ejection fraction (%)', 'Sodium (mmol/L)', 'eGFR in mL/min/1.73m²', 'Hemoglobin (g/dL)',
           'NT-proBNP in pg/mL', 'hs-cTnT in ng/L', 'ST2 (ng/mL)']
)


def check_values(parameter_value, parameter_name, min_max_median):
    lower_limit = min_max_median["lower_limit"][parameter_name]
    upper_limit = min_max_median["upper_limit"][parameter_name]
    median_impute = min_max_median["median_impute"][parameter_name]
    if parameter_value is None:
        parameter_value = median_impute if not math.isnan(median_impute) else None
    elif parameter_value < lower_limit:
        parameter_value = lower_limit
    elif parameter_value > upper_limit:
        parameter_value = upper_limit
    return parameter_value


def get_model(parameters):
    if ('NT-proBNP in pg/mL' in parameters and
            ('hs-cTnT in ng/L' not in parameters and 'ST2 (ng/mL)' not in parameters)):
        model = Model.MODEL_2
    elif ('hs-cTnT in ng/L' in parameters and
            ('NT-proBNP in pg/mL' not in parameters and 'ST2 (ng/mL)' not in parameters)):
        model = Model.MODEL_3
    elif ('ST2 (ng/mL)' in parameters and
          ('NT-proBNP in pg/mL' not in parameters and 'hs-cTnT in ng/L' not in parameters)):
        model = Model.MODEL_4
    elif (('NT-proBNP in pg/mL' in parameters and 'ST2 (ng/mL)' in parameters) and
          'hs-cTnT in ng/L' not in parameters):
        model = Model.MODEL_5
    elif (('NT-proBNP in pg/mL' in parameters and 'hs-cTnT in ng/L' in parameters) and
          'ST2 (ng/mL)' not in parameters):
        model = Model.MODEL_6
    elif (('hs-cTnT in ng/L' in parameters and 'ST2 (ng/mL)' in parameters) and
          'NT-proBNP in pg/mL' not in parameters):
        model = Model.MODEL_7
    elif 'NT-proBNP in pg/mL' in parameters and 'hs-cTnT in ng/L' in parameters and 'ST2 (ng/mL)' in parameters:
        model = Model.MODEL_8
    else:
        model = Model.MODEL_1
    return model


def get_coefficients(model, model_coefficients):
    if model == Model.MODEL_1:
        coefficients = model_coefficients['Model_1']
        sum_product = -8.9220
    elif model == Model.MODEL_2:
        coefficients = model_coefficients['Model_2']
        sum_product = -5.0910
    elif model == Model.MODEL_3:
        coefficients = model_coefficients['Model_3']
        sum_product = -2.7470
    elif model == Model.MODEL_4:
        coefficients = model_coefficients['Model_4']
        sum_product = -5.4690
    elif model == Model.MODEL_5:
        coefficients = model_coefficients['Model_5']
        sum_product = -3.3880
    elif model == Model.MODEL_6:
        coefficients = model_coefficients['Model_6']
        sum_product = -1.9810
    elif model == Model.MODEL_7:
        coefficients = model_coefficients['Model_7']
        sum_product = -0.445
    elif model == Model.MODEL_8:
        coefficients = model_coefficients['Model_8']
        sum_product = -0.237
    return coefficients, sum_product


def get_survival_estimate(target_param):
    if target_param == 1:
        survival_estimate = 0.942
    elif target_param == 2:
        survival_estimate = 0.875
    elif target_param == 3:
        survival_estimate = 0.802
    return survival_estimate


def get_new_parameters(parameters):
    new_parameters = dict({key: value for key, value in parameters.items()})
    new_parameters['NYHA Class'] = 0 if parameters['NYHA Class'] in [1, 2] else 1
    new_parameters['Ejection fraction (%)'] = 0 if parameters['Ejection fraction (%)'] < 45 else 1
    new_parameters['Furosemide Dose 1'] = 1 if parameters['Loop Diuretic Furosemide Dose'] <= 40 else 0
    new_parameters['Furosemide Dose 2'] = 1 if parameters['Loop Diuretic Furosemide Dose'] > 40 else 0
    new_parameters['log(NT-proBNP in pg/mL)'] = \
        0 if parameters['NT-proBNP in pg/mL'] == 0 else math.log(parameters['NT-proBNP in pg/mL'])
    new_parameters['log(hs-cTnT in ng/L)'] = \
        0 if parameters['hs-cTnT in ng/L'] == 0 else math.log(parameters['hs-cTnT in ng/L'])
    new_parameters['Squared log(hs-cTnT in ng/L)'] = math.pow(new_parameters['log(hs-cTnT in ng/L)'], 2)
    new_parameters['ST2_div_10'] = parameters['ST2 (ng/mL)'] / 10
    new_parameters['Squared ST2_div_10'] = math.pow(new_parameters['ST2_div_10'], 2)
    return new_parameters


def calc_barcelona_hf_score(parameters: Parameters) -> list[float]:
    scores = []
    coefficients_file = (ir.files(resources) / 'barcelona_hf_v1_coefficients.csv')
    with coefficients_file.open("rt", encoding="utf-8") as f:
        model_beta_coefficients = pd.read_csv(f, index_col='Variables')
    model = get_model(parameters)
    coefficients, sum_product = get_coefficients(model, model_beta_coefficients)

    for param in MIN_MAX_MEDIAN.index.to_list():
        parameters[param] = check_values(parameters[param], param, MIN_MAX_MEDIAN)  # type: ignore

    new_parameters = get_new_parameters(parameters)
    for year in range(1, 4):
        survival_estimate = get_survival_estimate(year)
        sum_product_all_parameters = sum(
            [new_parameters[parameter] * coeff for parameter, coeff in coefficients.items()]
        )
        score = (1 - math.pow(survival_estimate, math.exp(sum_product_all_parameters - sum_product))) * 100
        scores.append(round(score, 1))
    return scores
