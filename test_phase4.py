import unittest
from traceback import print_exc

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait


# NOTE: MUST HAVE SERVER RUNNING IN INCOGNITO WINDOW BEFORE RUNNING TESTS
class Phase4BugTests(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox(executable_path=r"C:\Users\chand\GIT_STUFF_GOES_HERE\EE461L\geckodriver.exe")
        self.driver.get("http://localhost:8080/equipment/1/INITIALIZE/None")
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "filter-open-button")))

    def tearDown(self):
        self.driver.close()

    # Triple Stacking Tests

    def test_TripleStackingServerError_SortSearchFilter(self):
        # Sort
        try:
            dropdown = Select(self.driver.find_element_by_id("equipmentsSortCriteriaMenu"))
            dropdown.select_by_value("price")
            self.driver.find_element_by_id("ascendBtn").click()
        except:
            print("ERROR\tSortSearchFilter\tException Caught During Sort")
            print_exc()
            self.fail()

        # Search
        try:
            searchbar = self.driver.find_element_by_id("searchBar")
            searchbar.send_keys("hi")
            searchbar.send_keys(Keys.ENTER)
        except:
            print("ERROR\tSortSearchFilter\tException Caught During Search")
            print_exc()
            self.fail()

        # Filter
        try:
            self.driver.find_element_by_class_name("filter-open-button").click()
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, "equipmentsOption1")))
            self.driver.find_element_by_id("equipmentsOption3").click()
            self.driver.find_element_by_id("equipmentsOption8").click()
            self.driver.find_element_by_name("Filter").click()
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "filter-open-button")))
        except:
            print("ERROR\tSortSearchFilter\tException Caught During Filter")
            print_exc()
            self.fail()

        # Check for Instances
        try:
            price = self.driver.find_element_by_id("priceText_0").text
            self.assertGreater(len(price), len("Price: "))
        except:
            print("ERROR\tSortSearchFilter\tNo Results Shown")
            print_exc()
            self.fail()

    def test_TripleStackingServerError_SortFilterSearch(self):
        # Sort
        try:
            dropdown = Select(self.driver.find_element_by_id("equipmentsSortCriteriaMenu"))
            dropdown.select_by_value("price")
            self.driver.find_element_by_id("ascendBtn").click()
        except:
            print("ERROR\tSortFilterSearch\tException Caught During Sort")
            print_exc()
            self.fail()

        # Filter
        try:
            self.driver.find_element_by_class_name("filter-open-button").click()
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, "equipmentsOption1")))
            self.driver.find_element_by_id("equipmentsOption3").click()
            self.driver.find_element_by_id("equipmentsOption8").click()
            self.driver.find_element_by_name("Filter").click()
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "filter-open-button")))
        except:
            print("ERROR\tSortFilterSearch\tException Caught During Filter")
            print_exc()
            self.fail()

        # Search
        try:
            searchbar = self.driver.find_element_by_id("searchBar")
            searchbar.send_keys("hi")
            searchbar.send_keys(Keys.ENTER)
        except:
            print("ERROR\tSortFilterSearch\tException Caught During Search")
            print_exc()
            self.fail()

        # Check for Instances
        try:
            price = self.driver.find_element_by_id("priceText_0").text
            self.assertGreater(len(price), len("Price: "))
        except:
            print("ERROR\tSortFilterSearch\tNo Results Shown")
            print_exc()
            self.fail()

    def test_TripleStackingServerError_SearchSortFilter(self):
        # Search
        try:
            searchbar = self.driver.find_element_by_id("searchBar")
            searchbar.send_keys("hi")
            searchbar.send_keys(Keys.ENTER)
        except:
            print("ERROR\tSearchSortFilter\tException Caught During Search")
            print_exc()
            self.fail()

        # Sort
        try:
            dropdown = Select(self.driver.find_element_by_id("equipmentsSortCriteriaMenu"))
            dropdown.select_by_value("price")
            self.driver.find_element_by_id("ascendBtn").click()
        except:
            print("ERROR\tSearchSortFilter\tException Caught During Sort")
            print_exc()
            self.fail()

        # Filter
        try:
            self.driver.find_element_by_class_name("filter-open-button").click()
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, "equipmentsOption1")))
            self.driver.find_element_by_id("equipmentsOption3").click()
            self.driver.find_element_by_id("equipmentsOption8").click()
            self.driver.find_element_by_name("Filter").click()
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "filter-open-button")))
        except:
            print("ERROR\tSearchSortFilter\tException Caught During Filter")
            print_exc()
            self.fail()

        # Check for Instances
        try:
            price = self.driver.find_element_by_id("priceText_0").text
            self.assertGreater(len(price), len("Price: "))
        except:
            print("ERROR\tSearchSortFilter\tNo Results Shown")
            print_exc()
            self.fail()

    def test_TripleStackingServerError_SearchFilterSort(self):
        # Search
        try:
            searchbar = self.driver.find_element_by_id("searchBar")
            searchbar.send_keys("hi")
            searchbar.send_keys(Keys.ENTER)
        except:
            print("ERROR\tSearchFilterSort\tException Caught During Search")
            print_exc()
            self.fail()

        # Filter
        try:
            self.driver.find_element_by_class_name("filter-open-button").click()
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, "equipmentsOption1")))
            self.driver.find_element_by_id("equipmentsOption3").click()
            self.driver.find_element_by_id("equipmentsOption8").click()
            self.driver.find_element_by_name("Filter").click()
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "filter-open-button")))
        except:
            print("ERROR\tSearchFilterSort\tException Caught During Filter")
            print_exc()
            self.fail()

        # Sort
        try:
            dropdown = Select(self.driver.find_element_by_id("equipmentsSortCriteriaMenu"))
            dropdown.select_by_value("price")
            self.driver.find_element_by_id("ascendBtn").click()
        except:
            print("ERROR\tSearchFilterSort\tException Caught During Sort")
            print_exc()
            self.fail()

        # Check for Instances
        try:
            price = self.driver.find_element_by_id("priceText_0").text
            self.assertGreater(len(price), len("Price: "))
        except:
            print("ERROR\tSearchFilterSort\tNo Results Shown")
            print_exc()
            self.fail()

    def test_TripleStackingServerError_FilterSortSearch(self):
        # Filter
        try:
            self.driver.find_element_by_class_name("filter-open-button").click()
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, "equipmentsOption1")))
            self.driver.find_element_by_id("equipmentsOption3").click()
            self.driver.find_element_by_id("equipmentsOption8").click()
            self.driver.find_element_by_name("Filter").click()
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "filter-open-button")))
        except:
            print("ERROR\tFilterSortSearch\tException Caught During Filter")
            print_exc()
            self.fail()

        # Sort
        try:
            dropdown = Select(self.driver.find_element_by_id("equipmentsSortCriteriaMenu"))
            dropdown.select_by_value("price")
            self.driver.find_element_by_id("ascendBtn").click()
        except:
            print("ERROR\tFilterSortSearch\tException Caught During Sort")
            print_exc()
            self.fail()

        # Search
        try:
            searchbar = self.driver.find_element_by_id("searchBar")
            searchbar.send_keys("hi")
            searchbar.send_keys(Keys.ENTER)
        except:
            print("ERROR\tFilterSortSearch\tException Caught During Search")
            print_exc()
            self.fail()

        # Check for Instances
        try:
            price = self.driver.find_element_by_id("priceText_0").text
            self.assertGreater(len(price), len("Price: "))
        except:
            print("ERROR\tFilterSortSearch\tNo Results Shown")
            print_exc()
            self.fail()

    def test_TripleStackingServerError_FilterSearchSort(self):
        # Filter
        try:
            self.driver.find_element_by_class_name("filter-open-button").click()
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, "equipmentsOption1")))
            self.driver.find_element_by_id("equipmentsOption3").click()
            self.driver.find_element_by_id("equipmentsOption8").click()
            self.driver.find_element_by_name("Filter").click()
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "filter-open-button")))
        except:
            print("ERROR\tFilterSearchSort\tException Caught During Filter")
            print_exc()
            self.fail()

        # Search
        try:
            searchbar = self.driver.find_element_by_id("searchBar")
            searchbar.send_keys("hi")
            searchbar.send_keys(Keys.ENTER)
        except:
            print("ERROR\tFilterSearchSort\tException Caught During Search")
            print_exc()
            self.fail()

        # Sort
        try:
            dropdown = Select(self.driver.find_element_by_id("equipmentsSortCriteriaMenu"))
            dropdown.select_by_value("price")
            self.driver.find_element_by_id("ascendBtn").click()
        except:
            print("ERROR\tFilterSearchSort\tException Caught During Sort")
            print_exc()
            self.fail()

        # Check for Instances
        try:
            price = self.driver.find_element_by_id("priceText_0").text
            self.assertGreater(len(price), len("Price: "))
        except:
            print("ERROR\tFilterSearchSort\tNo Results Shown")
            print_exc()
            self.fail()

    # Model Page Switching Tests
    def test_SwitchingBetweenModelPagesAfterPerformingOperations1(self):
        # Sort
        try:
            dropdown = Select(self.driver.find_element_by_id("equipmentsSortCriteriaMenu"))
            dropdown.select_by_value("price")
            self.driver.find_element_by_id("ascendBtn").click()
        except:
            print("ERROR\tBetweenModelPages1\tException Caught During Sort")
            print_exc()
            self.fail()

        # Search
        try:
            searchbar = self.driver.find_element_by_id("searchBar")
            searchbar.send_keys("hi")
            searchbar.send_keys(Keys.ENTER)
        except:
            print("ERROR\tBetweenModelPages1\tException Caught During Search")
            print_exc()
            self.fail()

        # Filter
        try:
            self.driver.find_element_by_class_name("filter-open-button").click()
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, "equipmentsOption1")))
            self.driver.find_element_by_id("equipmentsOption3").click()
            self.driver.find_element_by_id("equipmentsOption8").click()
            self.driver.find_element_by_name("Filter").click()
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "filter-open-button")))
        except:
            print("ERROR\tBetweenModelPages1\tException Caught During Filter")
            print_exc()
            self.fail()

        # Switch Pages
        self.driver.find_element_by_id("navExercises").click()
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "filter-open-button")))

        # Check for Instances
        try:
            instance0 = self.driver.find_element_by_id("exerciseCategoryTxt_0").text
            self.assertGreater(len(instance0), 0)
        except:
            print("ERROR\tBetweenModelPages1\tNo Results Shown")
            print_exc()
            self.fail()

    def test_SwitchingBetweenModelPagesAfterPerformingOperations2(self):
        # Search
        try:
            searchbar = self.driver.find_element_by_id("searchBar")
            searchbar.send_keys("hi")
            searchbar.send_keys(Keys.ENTER)
        except:
            print("ERROR\tBetweenModelPages1\tException Caught During Search")
            print_exc()
            self.fail()

        # Filter
        try:
            self.driver.find_element_by_class_name("filter-open-button").click()
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, "equipmentsOption1")))
            self.driver.find_element_by_id("equipmentsOption3").click()
            self.driver.find_element_by_id("equipmentsOption8").click()
            self.driver.find_element_by_name("Filter").click()
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "filter-open-button")))
        except:
            print("ERROR\tBetweenModelPages1\tException Caught During Filter")
            print_exc()
            self.fail()

        # Sort
        try:
            dropdown = Select(self.driver.find_element_by_id("equipmentsSortCriteriaMenu"))
            dropdown.select_by_value("price")
            self.driver.find_element_by_id("ascendBtn").click()
        except:
            print("ERROR\tBetweenModelPages1\tException Caught During Sort")
            print_exc()
            self.fail()

        # Switch Pages
        self.driver.find_element_by_id("navChannels").click()
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "filter-open-button")))

        # Check for Instances
        try:
            instance0 = self.driver.find_element_by_id("descriptionTxt_0").text
            self.assertGreater(len(instance0), 0)
        except:
            print("ERROR\tBetweenModelPages1\tNo Results Shown")
            print_exc()
            self.fail()


if __name__ == '__main__':
    unittest.main()
