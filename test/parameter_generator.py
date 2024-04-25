import random
from typing import Any, get_type_hints, Mapping

from acribis_scores import *


def __get_random_parameters__(parameter_dict: Mapping[str, Any]) -> dict[str, Any]:
    types = get_type_hints(parameter_dict)
    annotations = get_type_hints(parameter_dict, include_extras=True)
    random_parameters = {}
    for key, _ in parameter_dict.__annotations__.items():
        raw_parameter = types[key]
        annotation = annotations[key]
        metadata = getattr(annotation, '__metadata__', None)
        minimum = 0
        maximum = 100000
        if metadata:
            minimum = metadata[0].min
            maximum = metadata[0].max
        if raw_parameter == int:
            random_parameters[key] = random.randint(minimum, maximum)
        elif raw_parameter == float:
            random_parameters[key] = random.uniform(minimum, maximum)
        elif raw_parameter == bool:
            random_parameters[key] = bool(random.getrandbits(1))
        else:
            random_parameters[key] = None
    return random_parameters


def generate_chads_vasc_parameters() -> chads_vasc.Parameters:
    random_parameters = __get_random_parameters__(chads_vasc.Parameters)
    if random_parameters['Age ≥75y']:
        random_parameters['Age 65-74y'] = False
    return random_parameters


def generate_smart_parameters(creatinine: float) -> smart.Parameters:
    random_parameters = __get_random_parameters__(smart.Parameters)
    egfr = 186 * creatinine ** (-1.154) * random_parameters['Age in years'] ** (-0.203)
    if not random_parameters['Male']:
        egfr *= 0.742
    cvds: list[bool] = [bool(random.getrandbits(1)) for _ in range(4)]
    if not any(cvds):
        cvds[random.randint(0, 3)] = True
    random_parameters['History of coronary artery disease'] = cvds[0]
    random_parameters['History of cerebrovascular disease'] = cvds[1]
    random_parameters['Abdominal aortic aneurysm'] = cvds[2]
    random_parameters['Peripheral artery disease'] = cvds[3]
    random_parameters['eGFR in mL/min/1.73m²'] = egfr
    return random_parameters


def generate_maggic_parameters() -> maggic.Parameters:
    return __get_random_parameters__(maggic.Parameters)
