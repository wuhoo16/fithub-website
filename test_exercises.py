import unittest
import random

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


class TestHome(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox(executable_path=r"C:\Users\wenmi\Documents\UTAustin\Fall2020\EE461L_SoftwareLab\geckodriver.exe")
        # Start from Homepage and click into Exercises model page using NavBar
        self.driver.get("http://localhost:8080/")   
        self.driver.find_element_by_link_text("Exercises").click()

    def tearDown(self):
        self.driver.close()
    
    # Test Exercises Link in NavBar
    def test_exercise_page_directs_to_correct_page(self):
        self.assertEqual("Exercises Model Page", self.driver.title)

    # Test Text Components for Exercises on Model Page
    def test_exercise_has_category(self):
        category = self.driver.find_element_by_id("exerciseCategoryTxt_0").text
        category.replace("Category: ", "")
        self.assertNotEqual(0, len(category))

    def test_exercise_has_equipment(self):
        equipment = self.driver.find_element_by_id("exerciseEquipText_3").text
        equipment.replace("Equipment: ", "")
        self.assertNotEqual(0, len(equipment))

    def test_exercise_has_description(self):
        desc = self.driver.find_element_by_id("exerciseDescText_5").text
        desc.replace("Description: ", "")
        self.assertNotEqual(0, len(desc))

    # Testing validity of Instance Pages
    def test_instance_page_valid_1(self):
        name = self.driver.find_element_by_id("exerciseName_1").text
        self.driver.get("http://localhost:8080/exerciseinstance/1")   
        self.assertEqual(name, self.driver.title)

    def test_instance_page_valid_2(self):
        name = self.driver.find_element_by_id("exerciseName_4").text
        self.driver.get("http://localhost:8080/exerciseinstance/4")  
        self.assertEqual(name, self.driver.title)    

    # Testing Pagination
    def test_next_button(self):
        self.driver.get("http://localhost:8080/exercises/1")
        self.driver.find_element_by_link_text("Next").click()
        url = self.driver.current_url
        self.assertEqual("http://localhost:8080/exercises/2", url) 

    def test_random_page(self):
        page_num = random.randint(1, 13)
        self.driver.get("http://localhost:8080/exerciseinstance/" + str(page_num))  
        index = (page_num - 1)*9
        present = self.driver.find_elements_by_id("exerciseName_" + str(index))
        self.assertNotEqual(0, present)

if __name__ == '__main__':
    unittest.main()
