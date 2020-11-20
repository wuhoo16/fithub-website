import unittest
import random

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


class TestHome(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox(executable_path=r"C:\Users\wenmi\Documents\UTAustin\Fall2020\EE461L_SoftwareLab\geckodriver.exe")
        # Start from random Exercises instance page
        randNum = random.randint(0, 99)
        self.driver.get("http://localhost:8080/exerciseinstance/" + str(randNum))  

    def tearDown(self):
        self.driver.close()

    # Test Text Components for Exercises Instance Pages
    def test_exercise_has_category(self):
        category = self.driver.find_element_by_id("exerciseCategoryText").text
        category.replace("Category: ", "")
        self.assertNotEqual(0, len(category))

    def test_exercise_has_equipment(self):
        equipment = self.driver.find_element_by_id("exerciseEquipmentText").text
        equipment.replace("Equipment: ", "")
        self.assertNotEqual(0, len(equipment))

    def test_exercise_has_description(self):
        desc = self.driver.find_element_by_id("exerciseDescriptionText").text
        self.assertNotEqual(0, len(desc))   

    # Test existence of tables
    def test_instance_has_exercise_table1(self):
        exercise_table = self.driver.find_elements_by_id("exerciseTable1")
        self.assertNotEqual(0, len(exercise_table))

    def test_instance_has_exercise_table2(self):
        exercise_table = self.driver.find_elements_by_id("exerciseTable2")
        self.assertNotEqual(0, len(exercise_table))

    def test_instance_has_exercise_table3(self):
        exercise_table = self.driver.find_elements_by_id("exerciseTable3")
        self.assertNotEqual(0, len(exercise_table))


if __name__ == '__main__':
    unittest.main()
