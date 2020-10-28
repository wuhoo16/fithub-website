import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestHome(unittest.TestCase):
    
    def setUp(self):
        self.driver = webdriver.Firefox(executable_path=r"C:\Users\wenmi\Documents\UTAustin\Fall2020\EE461L_SoftwareLab\geckodriver.exe")
        # self.driver.get(r"file:///Users/kayleetrevino/Desktop/SoftwareLab/FitHubProject/TeamA13/templates/homepage.html")
        self.driver.get("http://localhost:8080/")

    def tearDown(self):
        self.driver.close()

    def test_start_at_home_page(self):
        self.assertEqual("Fithub Homepage", self.driver.title)  

    # Test Carousel Links
    def test_exercise_carousel_link(self):
        btn = self.driver.find_element_by_id("exerciseCarouselBtn")
        btn.click()
        self.assertEqual("Exercises Model Page", self.driver.title)

    def test_equipment_carousel_link(self):
        self.driver.find_element_by_id("carousel_next").click()
        element = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//a[@id='equipmentCarouselBtn']")))
        element.click()
        self.assertEqual("Equipment Model Page", self.driver.title)

    def test_channel_carousel_link(self):
        self.driver.find_element_by_id("carousel_prev").click()
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//a[@id='channelCarouselBtn']"))).click()
        self.assertEqual("Youtube Channel Model Page", self.driver.title)

    # Test NavBar Links
    def test_exercises_link(self):
        self.driver.find_element_by_link_text("Exercises").click()
        self.assertEqual("Exercises Model Page", self.driver.title) 

    def test_equipment_link(self):
        self.driver.find_element_by_link_text("Equipment").click()
        self.assertEqual("Equipment Model Page", self.driver.title)

    def test_channels_link(self):
        self.driver.find_element_by_link_text("Youtube Channels").click()
        self.assertEqual("Youtube Channel Model Page", self.driver.title) 

    def test_aboutme_link(self):
        self.driver.find_element_by_link_text("About").click()
        self.assertEqual("About Me Page", self.driver.title)            


if __name__ == '__main__':
    unittest.main()