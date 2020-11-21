import random
import unittest

from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


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
        self.driver.find_element_by_id("ascendBtn").click()
        randNumOne = random.randint(0, 7)
        randNumTwo = randNumOne + 1
        nameLess = self.driver.find_element_by_id("name_" + str(randNumOne)).text
        nameMore = self.driver.find_element_by_id("name_" + str(randNumTwo)).text
        print(nameMore + "\n" + nameLess)
        self.assertLessEqual(nameLess, nameMore)

    def test_sortOperation_PriceAscending(self):
        sortDropDown = Select(self.driver.find_element_by_id("equipmentsSortCriteriaMenu"))
        sortDropDown.select_by_value("price")
        self.driver.find_element_by_id("ascendBtn").click()
        randNumOne = random.randint(0, 7)
        randNumTwo = randNumOne + 1
        priceLess = float(self.driver.find_element_by_id("priceText_" + str(randNumOne)).text[7:-4])
        priceMore = float(self.driver.find_element_by_id("priceText_" + str(randNumTwo)).text[7:-4])
        self.assertLessEqual(priceLess, priceMore)

    def test_sortOperation_CategoryAscending(self):
        sortDropDown = Select(self.driver.find_element_by_id("equipmentsSortCriteriaMenu"))
        sortDropDown.select_by_value("category")
        self.driver.find_element_by_id("ascendBtn").click()
        randNumOne = random.randint(0, 7)
        randNumTwo = randNumOne + 1
        categoryLess = self.driver.find_element_by_id("categoryText_" + str(randNumOne)).text
        categoryMore = self.driver.find_element_by_id("categoryText_" + str(randNumTwo)).text
        self.assertLessEqual(categoryLess, categoryMore)

    def test_sortOperation_NameDescending(self):
        self.driver.find_element_by_id("descendBtn").click()
        randNumOne = random.randint(0, 7)
        randNumTwo = randNumOne + 1
        nameMore = self.driver.find_element_by_id("name_" + str(randNumOne)).text
        nameLess = self.driver.find_element_by_id("name_" + str(randNumTwo)).text
        print(nameMore + "\n" + nameLess)
        self.assertLessEqual(nameLess, nameMore)

    def test_sortOperation_PriceDescending(self):
        sortDropDown = Select(self.driver.find_element_by_id("equipmentsSortCriteriaMenu"))
        sortDropDown.select_by_value("price")
        self.driver.find_element_by_id("descendBtn").click()
        randNumOne = random.randint(0, 7)
        randNumTwo = randNumOne + 1
        priceMore = float(self.driver.find_element_by_id("priceText_" + str(randNumOne)).text[7:-4])
        priceLess = float(self.driver.find_element_by_id("priceText_" + str(randNumTwo)).text[7:-4])
        self.assertLessEqual(priceLess, priceMore)

    def test_sortOperation_CategoryDescending(self):
        sortDropDown = Select(self.driver.find_element_by_id("equipmentsSortCriteriaMenu"))
        sortDropDown.select_by_value("category")
        self.driver.find_element_by_id("ascendBtn").click()
        randNumOne = random.randint(0, 7)
        randNumTwo = randNumOne + 1
        categoryMore = self.driver.find_element_by_id("categoryText_" + str(randNumOne)).text
        categoryLess = self.driver.find_element_by_id("categoryText_" + str(randNumTwo)).text
        self.assertLessEqual(categoryLess, categoryMore)

    def test_stackedFilteringAfterSorting(self):
        # First emulate user sort in ascending order on the equipment price attribute
        sortDropDown = Select(self.driver.find_element_by_id("equipmentsSortCriteriaMenu"))
        sortDropDown.select_by_value("price")
        self.driver.find_element_by_id("ascendBtn").click()
        # Next try to filter on only equipments in the price range of 0 to 50$ and submit using the Filter button
        LOWER_PRICE_THRESHOLD = 0.00
        UPPER_PRICE_THRESHOLD = 50.00
        self.driver.find_element_by_id("openNavButton").click()
        self.driver.find_element_by_id("equipmentsOption1").click()
        self.driver.find_element_by_id("filterButton").click()
        # Verify that a randomly selected card on each page has the priceText_<0-8> HTML element between 0 and 50
        randNumOne = random.randint(0, 7)
        priceString = float(self.driver.find_element_by_id("priceText_" + str(randNumOne)).text[7:-4])
        self.assertTrue(priceString >= LOWER_PRICE_THRESHOLD)
        self.assertTrue(priceString < UPPER_PRICE_THRESHOLD)
        # Verify that two random subsequent cards are still in ascending order
        cardNum1 = random.randint(0, 7)
        cardNum2 = randNumOne + 1
        priceLess = float(self.driver.find_element_by_id("priceText_" + str(cardNum1)).text[7:-4])
        priceMore = float(self.driver.find_element_by_id("priceText_" + str(cardNum2)).text[7:-4])
        self.assertLessEqual(priceLess, priceMore)

    def test_filterByPrice(self):
        # Randomly select any of the filter by price checkboxes
        SELECTION_NUMBER = random.randint(1, 3)
        checkedFilter = self.driver.find_element_by_id("equipmentsOption" + str(SELECTION_NUMBER))
        priceRange = checkedFilter.get_attribute("value")
        LOWER_PRICE_THRESHOLD = float(priceRange.split()[0])
        UPPER_PRICE_THRESHOLD = float(priceRange.split()[1])
        self.driver.find_element_by_id("openNavButton").click()
        checkedFilter.click()
        self.driver.find_element_by_id("filterButton").click()
        # Verify that a randomly selected card has the priceText_<0-8> HTML element between the selected price thresholds
        cardNum = random.randint(0, 7)
        price = float(self.driver.find_element_by_id("priceText_" + str(cardNum)).text[7:-4])
        self.assertTrue(price >= LOWER_PRICE_THRESHOLD)
        self.assertTrue(price < UPPER_PRICE_THRESHOLD)

    def test_resetFiltersAndSorts(self):
        # Filter
        self.driver.find_element_by_class_name("filter-open-button").click()
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, "equipmentsOption1")))
        self.driver.find_element_by_id("equipmentsOption3").click()
        self.driver.find_element_by_id("equipmentsOption8").click()
        self.driver.find_element_by_name("Filter").click()
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "filter-open-button")))
        # Sort
        dropdown = Select(self.driver.find_element_by_id("equipmentsSortCriteriaMenu"))
        dropdown.select_by_value("price")
        self.driver.find_element_by_id("ascendBtn").click()
        # Search
        searchbar = self.driver.find_element_by_id("searchBar")
        searchbar.send_keys("hi")
        searchbar.send_keys(Keys.ENTER)
        # RESET ALL
        self.driver.find_element_by_id("resetBtn").click()
        # Check Filters are unchecked
        self.driver.find_element_by_class_name("filter-open-button").click()
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, "equipmentsOption1")))
        for x in range(8):
            self.assertFalse(self.driver.find_element_by_id("equipmentsOption" + str(x + 1)).is_selected())
        self.driver.find_element_by_class_name("closebtn").click()
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "filter-open-button")))
        # Check Sorting is default
        dropdown = Select(self.driver.find_element_by_id("equipmentsSortCriteriaMenu"))
        text = dropdown.first_selected_option.text
        self.assertEqual(text, "Sort by")
        # Check Searchbar is empty
        searchbar = self.driver.find_element_by_id("searchBar")
        self.assertEqual(searchbar.get_attribute('value'), "")


if __name__ == '__main__':
    unittest.main()
