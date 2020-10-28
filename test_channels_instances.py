import unittest

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

class TestHome(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Safari()
        self.driver.get("http://localhost:8080/channelinstance/6")

    def tearDown(self):
        self.driver.close()
    
    def test_instance_page_directs_to_correct_page(self):
        # Using holly dolke because later I know she doesnt have unsubscribed trailer
        # And need to test that it doesn't show up
        self.assertEqual("Holly Dolke", self.driver.title)

    def test_instance_has_exercise_table(self):
        exercise_table = self.driver.find_element_by_id("exerciseCaption_6").text
        self.assertNotEqual(0, len(exercise_table))

    def test_instance_has_equipment_table(self):
        equipment_table = self.driver.find_element_by_id("equipmentCaption_6").text
        self.assertNotEqual(0, len(equipment_table))
        
    def test_instance_has_channel_table(self):
        channel_table = self.driver.find_element_by_id("channelCaption_6").text
        self.assertNotEqual(0, len(channel_table))

    def test_instance_with_no_banner_url(self):
        try:
            url = self.driver.find_element_by_id("unsubscribedTrailerHeader_6")
            self.assertEqual(0, 1) #will automatically fail test
        except NoSuchElementException:
            pass

    def test_instance_topic_category_links(self):
        link = self.driver.find_element_by_id("channelTopicCategories_6_Lifestyle").get_attribute('href')
        self.assertEqual("https://en.wikipedia.org/wiki/Lifestyle_(sociology)", len(link))


if __name__ == '__main__':
    unittest.main()