import random
import unittest

from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys

# NOTE: MUST HAVE SERVER RUNNING IN INCOGNITO WINDOW BEFORE RUNNING TESTS

class JavaScriptTest(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox(executable_path=r"C:\Users\chand\GIT_STUFF_GOES_HERE\EE461L\geckodriver.exe")

    def tearDown(self):
        self.driver.close()

    def test_openNav(self):
        self.driver.get("http://localhost:8080/equipment/1")
        navbar = self.driver.find_element_by_id("mySidenav")
        self.driver.find_element_by_id("openNavButton").click()
        self.assertNotEqual(navbar.size['width'], 0)

    def test_closeNav(self):
        self.driver.get("http://localhost:8080/equipment/1")
        navbar = self.driver.find_element_by_id("mySidenav")
        self.driver.find_element_by_id("openNavButton").click()
        size1 = navbar.size["width"]
        self.driver.find_element_by_id("closeNavButton").click()
        size2 = navbar.size["width"]
        self.assertGreater(size1, size2)

    def test_verifyCheckBoxes(self):
        self.driver.get("http://localhost:8080/equipment/1")

        # fill out form with a few checkmarks
        self.driver.find_element_by_id("openNavButton").click()
        filterForm = self.driver.find_element_by_id("equipmentsFilterForm")
        checkboxes = filterForm.find_elements_by_tag_name("input")
        print("Checkboxes found: " + str(checkboxes))
        filterFormState1 = []
        alternator = 0
        for checkbox in checkboxes:
            alternator = alternator + 1
            if alternator == 1 or alternator == 5:
                checkbox.click()
                filterFormState1.append(checkbox)
                print(str(checkbox.is_selected()))
        self.driver.find_element_by_id("filterButton").click()

        # exit page and go back, save form state as another text
        self.driver.get("http://localhost:8080/exercises/1")
        self.driver.get("http://localhost:8080/equipment/1")
        self.driver.implicitly_wait(50000)
        self.driver.find_element_by_id("openNavButton").click()
        filterForm = self.driver.find_element_by_id("equipmentsFilterForm")
        checkboxes = filterForm.find_elements_by_tag_name("input")
        print("Checkboxes found: " + str(checkboxes))
        alternator = 0
        for checkbox in checkboxes:
            alternator = alternator + 1
            if alternator == 1 or alternator == 5:
                self.assertTrue(checkbox.is_selected())

    def test_resetCheckBoxState(self):
        self.driver.get("http://localhost:8080/equipment/1")

        # fill out form with a few checkmarks
        self.driver.find_element_by_id("openNavButton").click()
        filterForm = self.driver.find_element_by_id("equipmentsFilterForm")
        checkboxes = filterForm.find_elements_by_tag_name("input")
        print("Checkboxes found: " + str(checkboxes))
        alternator = 0
        for checkbox in checkboxes:
            if alternator == 1 or alternator == 5:
                checkbox.click()
            alternator = alternator + 1
        self.driver.find_element_by_id("filterButton").click()

        # reset checkmarks
        self.driver.get("http://localhost:8080/equipment/1")
        self.driver.implicitly_wait(50)
        self.driver.find_element_by_id("resetBtn").click()
        self.driver.implicitly_wait(50)
        self.driver.find_element_by_id("openNavButton").click()
        filterForm = self.driver.find_element_by_id("equipmentsFilterForm")
        checkboxes = filterForm.find_elements_by_tag_name("input")
        self.driver.implicitly_wait(250)
        print("Checkboxes found: " + str(checkboxes))
        alternator = 0
        for checkbox in checkboxes:
            print(alternator)
            self.assertFalse(checkbox.is_selected())
            alternator = alternator + 1

    def test_resetSearchSort(self):
        self.driver.get("http://localhost:8080/equipment/1")

        # get first results before anything
        object1_BEFORE = self.driver.find_element_by_id("name_0").text
        object2_BEFORE = self.driver.find_element_by_id("name_1").text
        print("object1_BEFORE = " + object1_BEFORE)
        print("object2_BEFORE = " + object2_BEFORE)

        # fill out search
        self.driver.find_element_by_id("searchBar").send_keys("ge")
        self.driver.find_element_by_id("searchBar").send_keys(Keys.RETURN)

        # sort by price
        sortDropDown = Select(self.driver.find_element_by_id("equipmentsSortCriteriaMenu"))
        sortDropDown.select_by_value("price")
        self.driver.find_element_by_id("descendBtn").click()
        object1_DURING = self.driver.find_element_by_id("name_0").text
        object2_DURING = self.driver.find_element_by_id("name_1").text
        print("object1_BEFORE = " + object1_DURING)
        print("object2_BEFORE = " + object2_DURING)

        # reset it all, check if was resetted
        self.driver.find_element_by_id("resetBtn").click()
        object1_AFTER = self.driver.find_element_by_id("name_0").text
        object2_AFTER = self.driver.find_element_by_id("name_1").text
        print("object1_BEFORE = " + object1_AFTER)
        print("object2_BEFORE = " + object2_AFTER)
        self.assertEquals(str(object1_BEFORE), str(object1_AFTER))
        self.assertEquals(str(object2_BEFORE), str(object2_AFTER))
        self.assertNotEquals(str(object1_DURING), str(object1_AFTER))
        self.assertNotEquals(str(object2_DURING), str(object2_AFTER))


if __name__ == '__main__':
    unittest.main()
