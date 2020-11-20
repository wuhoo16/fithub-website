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
        
    def test_channel_with_no_description_shows_placeholder(self):
        description = self.driver.find_element_by_id("descriptionTxt_8")
        self.assertEqual("Description: No description provided.", description.text)

    def test_channel_has_view_count(self):
        view_count = self.driver.find_element_by_id("viewTxt_8").text
        view_count = view_count.replace("Total Views: ", "")
        self.assertNotEqual(0, len(view_count))

    def test_channel_has_video_count(self):
        video_count = self.driver.find_element_by_id("videoTxt_8").text
        video_count = video_count.replace("Videos: ", "")
        self.assertNotEqual(0, len(video_count))

    def test_search_bar_starts_with_empty_text(self):
        text = self.driver.find_element_by_id("searchBar").get_attribute('value')
        self.assertEqual("", text)

    def test_sort_starts_with_default_value(self):
        sort_innerHTML = self.driver.find_element_by_id("channelsSortCriteriaMenu").get_attribute('innerHTML')
        sort_innerHTMLArr = sort_innerHTML.split("<option ")
        
        finalTxt = ""
        for innerStr in sort_innerHTMLArr:
            if "selected=" in innerStr:
                finalTxt = innerStr.split(">")[1].split("<")[0]
                break

        self.assertEqual("Select", finalTxt)

    def test_search_bar_resets_to_first_page_after_search(self):
        self.driver.find_element_by_link_text("Next").click()
        self.driver.execute_script("document.getElementById('searchBar').value = 'a';")
        self.driver.find_element_by_id("searchBar").click()
        url = self.driver.current_url
        self.assertEqual("a", self.driver.find_element_by_id('searchBar').get_attribute('value'))
        self.assertEqual("http://localhost:8080/channels/1", url)

    def test_search_bar_dropdown_is_hidden_on_page_reload(self):
        self.driver.execute_script("document.getElementById('searchBar').value = 'a';")
        self.driver.find_element_by_id("searchBar").click()
        items_visibility = self.driver.find_element_by_id("menuItems").is_displayed()
        self.assertEqual(False, items_visibility)

    def test_search_displays_dropdown_and_not_invalid_message_if_valid_search(self):
        self.driver.find_element_by_id("searchBar").send_keys('a')
        item_visibility = self.driver.find_element_by_id("menuItems").is_displayed()
        no_item_visibility = self.driver.find_element_by_id("empty").is_displayed()
        self.assertEqual(item_visibility, True)
        self.assertEqual(no_item_visibility, False)

    def test_invalid_search_input_gives_no_results_message(self):
        self.driver.find_element_by_id("searchBar").send_keys('aieehdd')
        no_item_visibility = self.driver.find_element_by_id("empty").is_displayed()
        self.assertEqual(no_item_visibility, True)


if __name__ == '__main__':
    unittest.main()