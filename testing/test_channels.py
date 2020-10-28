import unittest

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

class TestHome(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Safari()
        self.driver.get("http://localhost:8080/channels/1")

    def tearDown(self):
        self.driver.close()
    
    def test_channel_page_directs_to_correct_page(self):
        self.assertEqual("Youtube Channel Model Page", self.driver.title)

    def test_channel_has_subscriber_count(self):
        subscriber_count = self.driver.find_element_by_id("subscriberTxt_0").text
        subscriber_count.replace("Subscribers: ", "")
        self.assertNotEqual(0, len(subscriber_count))

    def test_channel_with_no_description_does_not_show_empty_string(self):
        try:
            description = self.driver.find_element_by_id("descriptionTxt_5")
            print(description.text)
            self.assertEqual(0, 1) #will automatically fail test
        except NoSuchElementException:
            pass
        
    def test_channel_with_no_description_shows_placeholder(self):
        description = self.driver.find_element_by_id("descriptionNoTxt_5")
        self.assertEqual("Description: No description provided.", description.text)

    def test_channel_has_view_count_and_video_count(self):
        view_count = self.driver.find_element_by_id("viewTxt_8").text
        view_count = view_count.replace("Total Views: ", "")
        self.assertNotEqual(0, len(view_count))

        video_count = self.driver.find_element_by_id("videoTxt_8").text
        video_count = video_count.replace("Videos: ", "")
        self.assertNotEqual(0, len(video_count))



if __name__ == '__main__':
    unittest.main()