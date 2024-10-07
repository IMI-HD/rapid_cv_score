import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By

from parameter_generator import generate_has_bled_parameters
from acribis_scores.has_bled import calc_has_bled_score


class TestHASBLEDCalculator(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()

    def tearDown(self):
        self.driver.quit()

    def test_has_bled(self):
        self.driver.maximize_window()
        for i in range(10):
            parameters = generate_has_bled_parameters()
            print(f"Run {i + 1}:\n{parameters}")
            self.driver.get("https://www.chadsvasc.org/")
            if parameters['Uncontrolled hypertension']:
                self.driver.find_element(By.CSS_SELECTOR, ".table2 .q0 > .td2 > div > div").click()
            if parameters['Abnormal Liver Function']:
                self.driver.find_element(By.CSS_SELECTOR, ".table2 .q1 > .td2 > div > div").click()
            if parameters['Abnormal Renal Function']:
                self.driver.find_element(By.CSS_SELECTOR, ".table2 .q2 > .td2").click()
            if parameters['Stroke']:
                self.driver.find_element(By.CSS_SELECTOR, ".table2 .q3 > .td2").click()
            if parameters['Bleeding history or predisposition']:
                self.driver.find_element(By.CSS_SELECTOR, ".table2 .q4 > .td2 > div > div").click()
            if parameters['Labile international normalized ratio (INR)']:
                self.driver.find_element(By.CSS_SELECTOR, ".table2 .q5 > .td2 > div > div").click()
            if parameters['Elderly']:
                self.driver.find_element(By.CSS_SELECTOR, ".table2 .q6 > .td2 > div > div").click()
            if parameters['Drugs Consumption']:
                self.driver.find_element(By.CSS_SELECTOR, ".table2 .q7 > .td2 > div > div").click()
            if parameters['Alcohol Consumption']:
                self.driver.find_element(By.CSS_SELECTOR, ".table2 .q8 > .td2 > div > div").click()
            element = self.driver.find_element(By.CSS_SELECTOR, ".result2 > div > div")
            online_score = int(element.text)
            score = calc_has_bled_score(parameters)
            self.assertEqual(online_score, score, 'HAS-BLED')


if __name__ == '__main__':
    unittest.main()
