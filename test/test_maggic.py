import time
import unittest

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

from test import parameter_generator
from acribis_scores.maggic import calc_maggic_score


class TestMAGGIC(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()

    def tearDown(self):
        self.driver.quit()

    def test_maggic(self):
        self.driver.get('http://www.heartfailurerisk.org/')
        self.driver.maximize_window()
        yes_no = {True: 'yes', False: 'no'}
        for i in range(10):
            parameters = parameter_generator.generate_maggic_parameters()
            accept_button = self.driver.find_element(By.ID, 'accept-terms')
            if accept_button.is_displayed():
                self.driver.find_element(By.ID, 'accept-terms').click()
                time.sleep(1)
            self.driver.find_element(By.ID, 'age').send_keys(str(parameters['Age (years)']))
            ActionChains(self.driver).move_by_offset(100, 0).click().perform()
            time.sleep(0.5)
            gender = 'Male' if parameters['Male'] else 'Female'
            dropdown = self.driver.find_element(By.ID, 'gender')
            dropdown.find_element(By.XPATH, f"//option[. = '{gender}']").click()
            self.driver.find_element(By.ID, f"diabetic-{yes_no[parameters['Diabetic']]}").click()
            self.driver.find_element(By.ID, f"copd-{yes_no[parameters['Diagnosis of COPD']]}").click()
            self.driver.find_element(By.ID,
                                     f"heart-failure-{yes_no[parameters['First diagnosis of heart failure in the past 18 months']]}").click()
            self.driver.find_element(By.ID, f"smoker-{yes_no[parameters['Current smoker']]}").click()
            dropdown = self.driver.find_element(By.ID, "nyha")
            dropdown.find_element(By.XPATH, f"//option[. = '{parameters['NYHA Class']}']").click()
            self.driver.find_element(By.ID, f"beta-blockers-{yes_no[not parameters['Not on beta blocker']]}").click()
            self.driver.find_element(By.ID, f"ace-{yes_no[not parameters['Not on ACEI/ARB']]}").click()
            self.driver.find_element(By.ID, "bmi").send_keys(str(parameters['BMI (kg/m²)']))
            self.driver.find_element(By.ID, "bp").send_keys(str(parameters['Systolic blood pressure (mmHg)']))
            self.driver.find_element(By.ID, "creatinine").send_keys(str(parameters['Creatinine (µmol/l)']))
            self.driver.find_element(By.ID, "ejection-fraction").send_keys(str(parameters['Ejection fraction (%)']))
            self.driver.find_element(By.ID, "calculate").click()
            time.sleep(1)
            online_score = int(self.driver.find_element(By.ID, "score-result").text)
            score = calc_maggic_score(parameters)
            self.assertEqual(online_score, score, 'MAGGIC')
            self.driver.find_element(By.ID, "form-return").click()
            time.sleep(1)
            self.driver.find_element(By.ID, "reset").click()
            time.sleep(1)


if __name__ == '__main__':
    unittest.main()
