import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By

from parameter_generator import generate_chads_vasc_parameters
from acribis_scores.chads_vasc import calc_chads_vasc_score


class TestCHADSVAScCalculator(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()

    def tearDown(self):
        self.driver.quit()

    def test_chads_vasc(self):
        self.driver.maximize_window()
        for i in range(10):
            parameters = generate_chads_vasc_parameters()
            self.driver.get("https://www.chadsvasc.org/")
            if parameters['Congestive heart failure/LV dysfunction']:
                self.driver.find_element(By.CSS_SELECTOR, ".table1 .q0 > .td2 > div > div").click()
            if parameters['Hypertension']:
                self.driver.find_element(By.CSS_SELECTOR, ".table1 .q1 > .td2 > div > div").click()
            if parameters['Age ≥75y']:
                self.driver.find_element(By.CSS_SELECTOR, ".table1 .q2 > .td2 > div > div").click()
            if parameters['Age 65-74y']:
                self.driver.find_element(By.CSS_SELECTOR, ".table1 .q3 > .td2 > div > div").click()
            if parameters['Diabetes mellitus']:
                self.driver.find_element(By.CSS_SELECTOR, ".table1 .q4 > .td2 > div > div").click()
            if parameters['Stroke/TIA/TE']:
                self.driver.find_element(By.CSS_SELECTOR, ".table1 .q5 > .td2 > div > div").click()
            if parameters['Vascular diseases']:
                self.driver.find_element(By.CSS_SELECTOR, ".table1 .q6 > .td2 > div > div").click()
            if parameters['Sex category']:
                self.driver.find_element(By.CSS_SELECTOR, ".table1 .q7 > .td2 > div > div").click()
            element = self.driver.find_element(By.CSS_SELECTOR, ".result1 > div > div")
            online_score = int(element.text)
            score = calc_chads_vasc_score(parameters)
            self.assertEqual(online_score, score, 'CHA2DS2-VASc')


if __name__ == '__main__':
    unittest.main()
