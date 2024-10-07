import math
import typing
from importlib import resources as ir
from typing import TypedDict, Any

import pandas as pd

from . import resources
from .barcelona_hf_v1 import check_values, get_model, Model

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
    'HF Duration in months': int,
    'Diabetes Mellitus': bool,
    'Hospitalisation Prev. Year': bool,
    'MRA': bool,
    'ICD': bool,
    'CRT': bool,
    'ARNI': bool,
    'NT-proBNP in pg/mL': typing.NotRequired[int],
    'hs-cTnT in ng/L': typing.NotRequired[float],
    'ST2 (ng/mL)': typing.NotRequired[float],
    'SGLT2i': bool,
})

#   The values in the min-max-median below is taken from the v3 disclaimer (terms of use).
MIN_MAX_MEDIAN = pd.DataFrame(
    {
        'lower_limit': [35, 11, 130, 6.4, 8.8, 21.5017, 3, 18.089, 0.5, 0],
        'upper_limit': [88, 71, 147, 109.7, 17.1, 34800.59, 265.45, 157.074, 246.948, 8],
        'median_impute': [70.3, 34, 139, 51.2, 12.9, 1361.5, 22.6, 38.1, 27, 0]
    },
    index=['Age (years)', 'Ejection fraction (%)', 'Sodium (mmol/L)', 'eGFR in mL/min/1.73m²',
           'Hemoglobin (g/dL)', 'NT-proBNP in pg/mL', 'hs-cTnT in ng/L', 'ST2 (ng/mL)',
           'HF Duration in months', 'Hospitalisation Prev. Year']
)


def get_coefficients(model, model_coefficients):
    coefficients = model_coefficients[model.name][:-6]
    sum_product = model_coefficients[model.name]['Sum_Product']
    return coefficients, sum_product


def get_survival_estimate(model, survival_year, model_coefficients) -> float:
    if survival_year == 1:
        survival_estimate = model_coefficients[model.name]['One_year_survival']
    elif survival_year == 2:
        survival_estimate = model_coefficients[model.name]['Two_year_survival']
    elif survival_year == 3:
        survival_estimate = model_coefficients[model.name]['Three_year_survival']
    elif survival_year == 4:
        survival_estimate = model_coefficients[model.name]['Four_year_survival']
    elif survival_year == 5:
        survival_estimate = model_coefficients[model.name]['Five_year_survival']
    return survival_estimate


def get_new_parameters(parameters):
    new_parameters = dict({key: value for key, value in parameters.items()})
    new_parameters['NYHA Class'] = 0 if parameters['NYHA Class'] in [1, 2] else 1
    new_parameters['Ejection fraction (%)'] = 0 if parameters['Ejection fraction (%)'] <= 45 else 1
    new_parameters['log(HF Duration in months)'] = math.log(parameters['HF Duration in months'])
    new_parameters['Furosemide Dose 1'] = 1 if 0 < parameters['Loop Diuretic Furosemide Dose'] <= 40 else 0
    new_parameters['Furosemide Dose 2'] = 1 if 40 < parameters['Loop Diuretic Furosemide Dose'] <= 80 else 0
    new_parameters['Furosemide Dose 3'] = 1 if parameters['Loop Diuretic Furosemide Dose'] > 80 else 0
    if 'NT-proBNP in pg/mL'in parameters:
        new_parameters['log(NT-proBNP in pg/mL)'] = \
            0 if parameters['NT-proBNP in pg/mL'] == 0 else math.log(parameters['NT-proBNP in pg/mL'])
    if 'hs-cTnT in ng/L' in parameters:
        new_parameters['log(hs-cTnT in ng/L)'] = \
            0 if parameters['hs-cTnT in ng/L'] == 0 else math.log(parameters['hs-cTnT in ng/L'])
        new_parameters['Squared log(hs-cTnT in ng/L)'] = math.pow(new_parameters['log(hs-cTnT in ng/L)'], 2)
    if 'ST2 (ng/mL)' in parameters:
        new_parameters['ST2_div_10'] = parameters['ST2 (ng/mL)'] / 10
        new_parameters['Squared ST2_div_10'] = math.pow(new_parameters['ST2_div_10'], 2)
    return new_parameters


def get_scores(file, model, new_parameters):
    scores = []
    with file.open('r', encoding='utf-8') as f:
        model_beta_coefficients = pd.read_csv(f, index_col='Variables')
    coefficients, sum_product = get_coefficients(model, model_beta_coefficients)
    sum_product_all_parameters = sum(
        [new_parameters[parameter] * coeff for parameter, coeff in coefficients.items() if parameter in new_parameters]
    )
    for year in range(1, 6):
        survival_estimate = get_survival_estimate(model, year, model_beta_coefficients)
        score = (1 - math.pow(survival_estimate, math.exp(sum_product_all_parameters - sum_product))) * 100
        scores.append(round(score, 1))
    return scores


def calc_life_expectancy(model, new_parameters):
    coefficients_life_expectancy = (ir.files(resources) / 'barcelona_hf_v3_life_expectancy_coefficients.csv')
    life_expectancy_limits = (ir.files(resources) / 'life_expectancy_limits.csv')
    with (coefficients_life_expectancy.open('r', encoding='utf-8') as f1,
          life_expectancy_limits.open('r', encoding='utf-8') as f2):
        le_coefficients = pd.read_csv(f1, index_col='Variables')
        le_limits = pd.read_csv(f2)
    coefficients = le_coefficients[model.name][:-2]
    sum_product_all_parameters = sum(
        [new_parameters[parameter] * coeff for parameter, coeff in coefficients.items() if parameter in new_parameters]
    )
    intercept = le_coefficients[model.name]['Intercept']
    gamma_value = le_coefficients[model.name]['Gamma Value']
    le = math.exp(intercept + sum_product_all_parameters) * gamma_value
    print(le)
    key = 'Women' if new_parameters['Female'] else 'Men'
    age = int(new_parameters['Age (years)'])
    if age in list(le_limits['Age']):
        if (key == 'Men' and age > 63) or (key == 'Women' and age > 67):
            upper_limit = le_limits.loc[le_limits['Age'] == int(new_parameters['Age (years)']), key].iloc[0]
            if le > float(upper_limit):
                le = upper_limit
    if le > 20:
        if key == 'Men' and age <= 63:
            le = '>20'
        elif key == 'Women' and age <= 67:
            le = '>20'
    return le


def _round_life_expectancy(model, parameters):
    life_expectancy = calc_life_expectancy(model, parameters)
    try:
        float(life_expectancy)
        life_expectancy = round(float(life_expectancy), 1)
    except:
        pass
    return life_expectancy


def calc_barcelona_hf_score(parameters: Parameters) -> dict[str, dict[str, list[float] | Any]]:
    all_scores = {}
    coefficients_death_file = (ir.files(resources) / 'barcelona_hf_v3_death_coefficients.csv')
    coefficients_hosp_file = (ir.files(resources) / 'barcelona_hf_v3_hosp_coefficients.csv')
    coefficients_hosp_death_file = (ir.files(resources) / 'barcelona_hf_v3_hosp_death_coefficients.csv')
    model = get_model(parameters)

    for param in MIN_MAX_MEDIAN.index.to_list():
        if param in parameters:
            parameters[param] = check_values(parameters[param], param, MIN_MAX_MEDIAN)  # type: ignore

    new_parameters = get_new_parameters(parameters)
    endpoints_without_biomarkers, endpoints_with_biomarkers = {}, {}
    for file in [coefficients_death_file, coefficients_hosp_file, coefficients_hosp_death_file]:
        suffix = file.name[16:-17]
        scores_without_biomarkers = get_scores(file, Model.MODEL_1, new_parameters)
        endpoints_without_biomarkers[suffix] = scores_without_biomarkers

        if model.name != 'MODEL_1':
            scores_with_biomarkers = get_scores(file, model, new_parameters)
            endpoints_with_biomarkers[suffix] = scores_with_biomarkers

        if file.name == 'barcelona_hf_v3_death_coefficients.csv':
            le_without_biomarkers = _round_life_expectancy(Model.MODEL_1, new_parameters)
            endpoints_without_biomarkers['life_expectancy'] = str(le_without_biomarkers)

            if model.name != 'MODEL_1':
                le_with_biomarkers = _round_life_expectancy(model, new_parameters)
                endpoints_with_biomarkers['life_expectancy'] = str(le_with_biomarkers)

    all_scores['without_biomarkers'] = endpoints_without_biomarkers
    if model.name != 'MODEL_1':
        all_scores['with_biomarkers'] = endpoints_with_biomarkers

    return all_scores
