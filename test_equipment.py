import random
import unittest

from selenium import webdriver
from selenium.webdriver.support.select import Select


# NOTE: MUST HAVE SERVER RUNNING IN INCOGNITO WINDOW BEFORE RUNNING TESTS
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
        print(randNum)
        link = self.driver.find_element_by_id("instancePageLink_" + str(randNum)).get_attribute('href')
        self.assertEqual("http://localhost:8080/equipmentinstance/" + str(randNum), link)

    # Testing Sort Operation
    def test_sortOperation_NameAscending(self):
        self.driver.find_element_by_id("equipmentAscending").click()
        randNumOne = random.randint(0, 7)
        randNumTwo = randNumOne + 1
        nameLess = self.driver.find_element_by_id("name_" + str(randNumOne)).text
        nameMore = self.driver.find_element_by_id("name_" + str(randNumTwo)).text
        print(nameMore + "\n" + nameLess)
        self.assertLessEqual(nameLess, nameMore)

    def test_sortOperation_PriceAscending(self):
        sortDropDown = Select(self.driver.find_element_by_id("equipmentsSortCriteriaMenu"))
        sortDropDown.select_by_value("price")
        self.driver.find_element_by_id("equipmentAscending").click()
        randNumOne = random.randint(0, 7)
        randNumTwo = randNumOne + 1
        priceLess = float(self.driver.find_element_by_id("priceText_" + str(randNumOne)).text[7:-4])
        priceMore = float(self.driver.find_element_by_id("priceText_" + str(randNumTwo)).text[7:-4])
        self.assertLessEqual(priceLess, priceMore)

    def test_sortOperation_CategoryAscending(self):
        sortDropDown = Select(self.driver.find_element_by_id("equipmentsSortCriteriaMenu"))
        sortDropDown.select_by_value("category")
        self.driver.find_element_by_id("equipmentAscending").click()
        randNumOne = random.randint(0, 7)
        randNumTwo = randNumOne + 1
        categoryLess = self.driver.find_element_by_id("categoryText_" + str(randNumOne)).text
        categoryMore = self.driver.find_element_by_id("categoryText_" + str(randNumTwo)).text
        self.assertLessEqual(categoryLess, categoryMore)

    def test_sortOperation_NameDescending(self):
        self.driver.find_element_by_id("equipmentDescending").click()
        randNumOne = random.randint(0, 7)
        randNumTwo = randNumOne + 1
        nameMore = self.driver.find_element_by_id("name_" + str(randNumOne)).text
        nameLess = self.driver.find_element_by_id("name_" + str(randNumTwo)).text
        print(nameMore + "\n" + nameLess)
        self.assertLessEqual(nameLess, nameMore)

    def test_sortOperation_PriceDescending(self):
        sortDropDown = Select(self.driver.find_element_by_id("equipmentsSortCriteriaMenu"))
        sortDropDown.select_by_value("price")
        self.driver.find_element_by_id("equipmentDescending").click()
        randNumOne = random.randint(0, 7)
        randNumTwo = randNumOne + 1
        priceMore = float(self.driver.find_element_by_id("priceText_" + str(randNumOne)).text[7:-4])
        priceLess = float(self.driver.find_element_by_id("priceText_" + str(randNumTwo)).text[7:-4])
        self.assertLessEqual(priceLess, priceMore)

    def test_sortOperation_CategoryDescending(self):
        sortDropDown = Select(self.driver.find_element_by_id("equipmentsSortCriteriaMenu"))
        sortDropDown.select_by_value("category")
        self.driver.find_element_by_id("equipmentAscending").click()
        randNumOne = random.randint(0, 7)
        randNumTwo = randNumOne + 1
        categoryMore = self.driver.find_element_by_id("categoryText_" + str(randNumOne)).text
        categoryLess = self.driver.find_element_by_id("categoryText_" + str(randNumTwo)).text
        self.assertLessEqual(categoryLess, categoryMore)

    # TODO: write filtering test cases
    # def test_stackedFilteringAFterSorting(self):
    #     //  filter by X
    #
    # def test_resetFiltersAndSorts(self):
    #     self.driver.find_element_by_id("resetButton").click()
    #
    #
    # def test_filterBy____(self):
    #     self.driver.find_element_by_id("resetButton").click()
    #     //  filter by X


if __name__ == '__main__':
    unittest.main()
