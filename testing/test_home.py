import unittest

from selenium import webdriver

class TestHome(unittest.TestCase):
    
    def setUp(self):
        self.driver = webdriver.Safari()
        # self.driver.get(r"file:///Users/kayleetrevino/Desktop/SoftwareLab/FitHubProject/TeamA13/templates/homepage.html")
        self.driver.get("http://localhost:8080/")

    def tearDown(self):
        self.driver.close()

    def test_start_at_home_page(self):
        self.assertEqual("Fithub Homepage", self.driver.title)

    def test_exercise_carousel_link(self):
        btn = self.driver.find_element_by_id("exerciseCarouselBtn")
        print(self.driver.current_url)
        btn.click()
        self.driver.implicitly_wait(60)
        print(self.driver.current_url)

        self.assertEqual("Exercises Model Page", self.driver.title)

    # def test_equipment_carousel_link():
    #     btn = self.driver.find_element_by_id("equipmentCarouselBtn")
    #     btn.click()

    #     assertEquals("Equipment Model Page", driver.getTitle())

    # def test_channel_carousel_link():
    #     btn = self.driver.find_element_by_id("channelCarouselBtn")
    #     btn.click()

    #     assertEquals("Youtube Channel Model Page", driver.getTitle())



if __name__ == '__main__':
    unittest.main()