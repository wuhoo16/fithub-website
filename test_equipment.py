import random
import unittest

from selenium import webdriver


class EquipmentTest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox(executable_path=r"C:\Users\chand\GIT_STUFF_GOES_HERE\EE461L\geckodriver.exe")
        self.driver.get("http://localhost:8080/equipment/1")

    def tearDown(self):
        self.driver.close()

    def test_directsToCorrectPage(self):
        self.assertEqual("Equipment Model Page", self.driver.title)

    def test_equipmentHasPrice(self):
        randNum = random.randint(0, 8)
        price = self.driver.find_element_by_id("priceText_" + str(randNum)).text
        self.assertGreater(len(price), len("Price: "))

    def test_equipmentHasCategory(self):
        randNum = random.randint(0, 8)
        category = self.driver.find_element_by_id("categoryText_" + str(randNum)).text
        self.assertGreater(len(category), len("Category: "))

    def test_equipmentHasSellerLocation(self):
        randNum = random.randint(0, 8)
        location = self.driver.find_element_by_id("sellerLocationText_" + str(randNum)).text
        self.assertGreater(len(location), len("Seller Location: "))

    def test_cardHasLink(self):
        randNum = random.randint(0, 8)
        link = self.driver.find_element_by_id("instancePageLink_" + str(randNum)).get_attribute('href')
        self.assertGreater(len(str(link)), 0)

    def test_cardLinksToCorrectInstancePage(self):
        randNum = random.randint(0, 8)
        link = self.driver.find_element_by_id("instancePageLink_" + str(randNum)).get_attribute('href')
        self.assertEqual("http://localhost:8080/equipmentinstance/" + str(randNum), link)


if __name__ == '__main__':
    unittest.main()
