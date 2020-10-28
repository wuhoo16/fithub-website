import random
import unittest

from selenium import webdriver


class EquipmentTest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox(executable_path=r"C:\Users\chand\GIT_STUFF_GOES_HERE\EE461L\geckodriver.exe")
        randNum = random.randint(0, 8)
        self.driver.get("http://localhost:8080/equipmentinstance/" + str(randNum))

    def tearDown(self):
        self.driver.close()

    def test_instanceDirectsToCorrectPage(self):
        instanceName = self.driver.find_element_by_id("equipmentInstanceName").text
        self.assertEqual(instanceName, "Name: " + self.driver.title)

    def test_instancePageDisplaysPrice(self):
        price = self.driver.find_element_by_id("priceText").text
        self.assertGreater(len(price), len("Price:  USD"))

    def test_instancePageDisplaysSellerLocation(self):
        sellerLocation = self.driver.find_element_by_id("sellerLocationText").text
        self.assertGreater(len(sellerLocation), len("Seller Location:  "))

    def test_instancePageDisplaysCategory(self):
        category = self.driver.find_element_by_id("categoryText").text
        self.assertGreater(len(category), len("Category: "))


if __name__ == '__main__':
    unittest.main()
