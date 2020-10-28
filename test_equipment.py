import unittest

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class EquipmentTest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox(executable_path=r"C:\Users\chand\GIT_STUFF_GOES_HERE\EE461L\TeamA13\geckodriver.exe")
        self.driver.get("http://localhost:8080")

    def tearDown(self):
        self.driver.close()

    def test_DirectsToCorrectPage(self):
        self.assertEqual("Equipment Model Page", self.driver.title)

    # TODO: this
    def test_ModelHasCorrectNumberOfInstances(self, correctNum):
        equipmentList = self.driver.find_element_by_id("equipmentArray")

    # TODO: this
    def test_EquipmentHasPrice(self):
        # check if has price

    # TODO: this
    def test_EquipmentHasCategory(self):
        # check if has category

    # TODO: this
    def test_EquipmentHasSellerLocation(self):
        # check if has seller location

    def test_

if __name__ == '__main__':test
    unittest.main()