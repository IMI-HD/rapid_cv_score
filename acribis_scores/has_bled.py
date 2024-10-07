from typing import TypedDict

# See: https://academic.oup.com/eurheartj/article/42/5/373/5899003


Parameters = TypedDict('Parameters', {
    'Uncontrolled hypertension': bool,
    'Abnormal Renal Function': bool,
    'Abnormal Liver Function': bool,
    'Stroke': bool,
    'Bleeding history or predisposition': bool,
    'Labile international normalized ratio (INR)': bool,
    'Elderly': bool,
    'Drugs Consumption': bool,
    'Alcohol Consumption': bool,
})


def calc_has_bled_score(parameters: Parameters) -> int:
    return sum(parameters.values())
