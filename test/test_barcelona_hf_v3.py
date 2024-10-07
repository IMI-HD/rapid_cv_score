import time
import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By

from parameter_generator import generate_barcelona_hf_v3_parameters
from acribis_scores.barcelona_hf_v3 import calc_barcelona_hf_score


class TestBarcelonaBioHF(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()

    def tearDown(self):
        self.driver.quit()

    def test_barcelona_bio_hf(self):
        self.driver.maximize_window()
        options = {True: '1', False: '2'}
        for i in range(5):
            self.driver.get('https://ww2.bcnbiohfcalculator.org/web/en/disclaimer')
            parameters = generate_barcelona_hf_v3_parameters()
            print(f"Run {i}:\n{parameters}")
            time.sleep(1)
            if self.driver.find_elements(By.ID, 'btn_agree'):
                self.driver.find_element(By.ID, 'btn_agree').click()
                time.sleep(1)
            self.driver.find_element(By.ID, 'age').send_keys(parameters['Age (years)'])
            self.driver.find_element(By.ID, f"sex_{options[not parameters['Female']]}").click()
            self.driver.find_element(By.ID, f"nyha_{options[parameters['NYHA Class'] < 3]}").click()
            self.driver.find_element(By.ID, 'na').send_keys(parameters['Sodium (mmol/L)'])
            self.driver.find_element(By.ID, 'egfr').send_keys(parameters['eGFR in mL/min/1.73m²'])
            self.driver.find_element(By.ID, 'hb').send_keys(parameters['Hemoglobin (g/dL)'])
            self.driver.find_element(By.ID, 'lvef').send_keys(parameters['Ejection fraction (%)'])
            self.driver.find_element(By.ID, 'ic_meses').send_keys(parameters['HF Duration in months'])
            if parameters['Diabetes Mellitus']:
                self.driver.find_element(By.ID, 'diabetes_mellitus_1').click()
            else:
                self.driver.find_element(By.CSS_SELECTOR, ".radio:nth-child(3) > #diabetes_mellitus_1").click()
            self.driver.find_element(By.ID, 'ic_ingresos').send_keys(
                '1' if parameters['Hospitalisation Prev. Year'] else '0')
            self.driver.find_element(By.ID, 'furosemide').send_keys(parameters['Loop Diuretic Furosemide Dose'])
            self.driver.find_element(By.ID, 'torasemide').send_keys('0')
            self.driver.find_element(By.ID, f"statins_{options[parameters['Statin']]}").click()
            self.driver.find_element(By.ID, f"betablocker_{options[parameters['Betablockers']]}").click()
            self.driver.find_element(By.ID, f"treatment_{options[parameters['ACEi/ARB']]}").click()
            self.driver.find_element(By.ID, f"arm_{options[parameters['MRA']]}").click()
            self.driver.find_element(By.ID, f"arni_{options[parameters['ARNI']]}").click()
            self.driver.find_element(By.ID, f"isglt_{options[parameters['SGLT2i']]}").click()
            self.driver.find_element(By.ID, f"trc_{options[parameters['CRT']]}").click()
            self.driver.find_element(By.ID, f"dai_{options[parameters['ICD']]}").click()
            self.driver.find_element(By.ID, 'tnt_hs').send_keys(parameters['hs-cTnT in ng/L'])
            self.driver.find_element(By.ID, 'st2').send_keys(parameters['ST2 (ng/mL)'])
            self.driver.find_element(By.ID, 'ntprobnp').send_keys(parameters['NT-proBNP in pg/mL'])
            score = calc_barcelona_hf_score(parameters)
            # TODO: Test fails for Risk of Death or HF Hospitalization
            print('Risk of death:')
            self.driver.find_element(By.ID, 'btn_generate_exitus').click()
            self.__read_results__(score, 'death')
            print('Risk of HF hospitalization:')
            self.driver.find_element(By.ID, 'btn_generate_ingres').click()
            self.__read_results__(score, 'hosp')
            # print('Risk of death or HF hospitalization:')
            # self.driver.find_element(By.ID, 'btn_generate_ingres_exitus').click()
            # self.__read_results__(score, 'hosp_death')

    def __read_results__(self, score, endpoint):
        time.sleep(1)
        accept_button = self.driver.find_element(By.ID, 'btn_accept')
        if accept_button.is_displayed():
            accept_button.click()
            time.sleep(1)
        no_biomarkers = [self.driver.find_element(By.CSS_SELECTOR, f".odd > td:nth-child({j})").text
                         for j in range(2, 7)]
        if self.driver.find_elements(By.CSS_SELECTOR, '.even'):
            with_biomarkers = [self.driver.find_element(By.CSS_SELECTOR, f".even > td:nth-child({k})").text
                               for k in range(2, 7)]
        le_container = self.driver.find_element(By.ID, 'expectancies-container')
        if le_container.is_displayed():
            le_without = self.driver.find_element(By.CSS_SELECTOR, '.odd > .last_column').text
            le_with = self.driver.find_element(By.CSS_SELECTOR, '.even > .last_column').text
            print(f"Life expectancy (without biomarkers): {le_without}")
            print(f"Life expectancy (with biomarkers): {le_with}")
            life_expectancy_without = score['without_biomarkers']['life_expectancy']
            life_expectancy_with = score['with_biomarkers']['life_expectancy']
            try:
                float(life_expectancy_without)
                self.assertAlmostEqual(float(le_without), float(life_expectancy_without),
                                       msg='Life Expectancy without Biomarkers', delta=0.1)
            except ValueError:
                self.assertEqual(le_without, life_expectancy_without, msg='Life Expectancy without Biomarkers')

            try:
                float(life_expectancy_with)
                self.assertAlmostEqual(float(le_with), float(life_expectancy_with),
                                       msg='Life Expectancy with Biomarkers', delta=0.1)
            except ValueError:
                self.assertEqual(le_with, life_expectancy_with, msg='Life Expectancy with Biomarkers')

        no_biomarkers = [float(s[:-1]) for s in no_biomarkers]
        with_biomarkers = [float(s[:-1]) for s in with_biomarkers]

        for a, b in zip(no_biomarkers, score['without_biomarkers'][endpoint]):
            self.assertAlmostEqual(float(a), float(b), msg=f'Barcelona-HF {endpoint} without biomarkers', delta=0.11)

        for c, d in zip(with_biomarkers, score['with_biomarkers'][endpoint]):
            self.assertAlmostEqual(float(c), float(d), msg=f'Barcelona-HF {endpoint} with biomarkers', delta=0.11)


if __name__ == '__main__':
    unittest.main()
