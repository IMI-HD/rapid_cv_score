import random
import time
import unittest
import requests

from parameter_generator import generate_smart_parameters
from acribis_scores.smart import calc_smart_score


class TestSMARTCalculator(unittest.TestCase):
    def test_smart(self):
        for i in range(10):
            creatinine = random.uniform(0.57, 2.26)
            parameters = generate_smart_parameters(creatinine)
            cvds = {'coronaryArteryDisease': parameters['History of coronary artery disease'],
                    'cerebrovascularDisease': parameters['History of cerebrovascular disease'],
                    'peripheralArteryDisease': parameters['Peripheral artery disease'],
                    'aorticAneurysm': parameters['Abdominal aortic aneurysm']}
            json = {
                "age": {
                    "unit": "years",
                    "value": str(parameters['Age in years'])
                },
                "cardiovascularDiseases": [name for name, value in cvds.items() if value],
                "creatinin": {
                    "unit": "mg/dL",
                    "value": str(creatinine)
                },
                "crp": {
                    "unit": "mg/L",
                    "value": str(parameters['hs-CRP in mg/dL'])
                },
                "diabetesDiagnosis": parameters['Diabetic'],
                "hdlCholesterol": {
                    "unit": "mmol/L",
                    "value": str(parameters['HDL-cholesterol in mmol/L'])
                },
                "historyCVD": "1",
                "id": "smartScore",
                "isSmoking": parameters['Current smoker'],
                "isSmokingFuture": parameters['Current smoker'],
                "ldlCholesterol": {
                    "unit": "mmol/L",
                    "value": "0.1"
                },
                "ldlMax": 8,
                "sbp": {
                    "unit": "mmHg",
                    "value": str(parameters['Systolic blood pressure in mmHg'])
                },
                "sex": "M" if parameters['Male'] else "F",
                "totalCholesterol": {
                    "unit": "mmol/L",
                    "value": parameters['Total cholesterol in mmol/L']
                },
                "usingAnticoag": parameters['Antithrombotic treatment'],
                "usingAnticoagFuture": parameters['Antithrombotic treatment'],
                "yearsSinceFirstDiagnosis": {
                    "unit": "years",
                    "value": str(parameters['Years since first diagnosis of vascular disease'])
                }
            }

            x = requests.post('https://uprevent-prod-api.azurewebsites.net/api/RiskCalculation/calculate', json=json)
            u_prevent_score = x.json()['tenYearRisk']['risk']
            score = calc_smart_score(parameters)
            self.assertAlmostEqual(score, u_prevent_score, msg='SMART Score', delta=0.01)
            time.sleep(0.5)


if __name__ == '__main__':
    unittest.main()
