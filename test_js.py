import random
import unittest

from selenium import webdriver


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
        checkboxes = filterForm.find_elements_by_tag_name("label")
        print("Checkboxes found: " + str(checkboxes))
        filterFormState1 = []
        alternator = 0
        for checkbox in checkboxes:
            alternator = alternator + 1
            if alternator == 1 or alternator == 5:
                checkbox.click()
                filterFormState1.append(checkbox)
        self.driver.find_element_by_id("filterButton").click()

        # exit page and go back, save form state as another text
        self.driver.get("http://localhost:8080/exercises/1")
        self.driver.get("http://localhost:8080/equipment/1")
        self.driver.implicitly_wait(50000)
        self.driver.find_element_by_id("openNavButton").click()
        filterForm = self.driver.find_element_by_id("equipmentsFilterForm")
        checkboxes = filterForm.find_elements_by_tag_name("label")
        print("Checkboxes found: " + str(checkboxes))
        alternator = 0
        for checkbox in checkboxes:
            alternator = alternator + 1
            if alternator == 1 or alternator == 5:
                self.assertTrue(checkbox.is_enabled())

    def test_resetCheckBoxState(self):
        self.driver.get("http://localhost:8080/equipment/1")

        # fill out form with a few checkmarks
        self.driver.find_element_by_id("openNavButton").click()
        filterForm = self.driver.find_element_by_id("equipmentsFilterForm")
        checkboxes = filterForm.find_elements_by_tag_name("label")
        print("Checkboxes found: " + str(checkboxes))
        alternator = 0
        for checkbox in checkboxes:
            alternator = alternator + 1
            if alternator == 1 or alternator == 5:
                checkbox.click()
        self.driver.find_element_by_id("filterButton").click()

        # reset checkmarks
        self.driver.get("http://localhost:8080/equipment/1")
        self.driver.implicitly_wait(50000)
        self.driver.find_element_by_id("openNavButton").click()
        self.driver.find_element_by_id("resetButton").click()
        self.driver.implicitly_wait(50000)
        self.driver.find_element_by_id("openNavButton").click()
        filterForm = self.driver.find_element_by_id("equipmentsFilterForm")
        checkboxes = filterForm.find_elements_by_tag_name("label")
        print("Checkboxes found: " + str(checkboxes))
        alternator = 0
        for checkbox in checkboxes:
            print(alternator)
            self.assertFalse(checkbox.is_enabled())


    def resetSearchSort(self):
        self.driver.get("http://localhost:8080/equipment/1")

        # fill out search
        self.driver.find_element_by_id("searchBar").send_keys("g")
        searchResults = self.driver.find_element_by_id("menuItems")
        searchResults[0].click()



    def test_clearLocalStorage(self):


if __name__ == '__main__':
    unittest.main()
