import unittest
import main

from pymongo import MongoClient
from unittest import TestCase
unittest.TestLoader.sortTestMethodsUsing = None


class TestMain(TestCase):
    @classmethod
    def setUpClass(cls):
        print('Setting up before TestMain class...')
        # Note we will use a different database during unit testing to avoid corrupting our actual database
        cls.TEST_DATABASE_NAME = 'test_phase2Database'
        client = MongoClient("mongodb+srv://Admin:Pass1234@apidata.lr4ia.mongodb.net/test_phase2Database?retryWrites=true&w=majority")
        client.drop_database(cls.TEST_DATABASE_NAME)
        cls.TEST_DATABASE = client[cls.TEST_DATABASE_NAME]
        cls.EXERCISE_COLLECTION_NAME = "exercises"
        cls.EQUIPMENT_COLLECTION_NAME = "equipments"
        cls.CHANNEL_COLLECTION_NAME = "channels"

    @classmethod
    def tearDownClass(cls):
        print(f"Tearing down after TestMain class...")
        client = MongoClient("mongodb+srv://Admin:Pass1234@apidata.lr4ia.mongodb.net/test_phase2Database?retryWrites=true&w=majority")
        client.drop_database(cls.TEST_DATABASE_NAME)
        if cls.TEST_DATABASE_NAME not in client.list_database_names():
            print(f"Database named { cls.TEST_DATABASE_NAME } successfully dropped!")

    # TEST ALL DATABASE INITIALIZATION AND LOADING METHODS: Create, Read, and Delete operations on the 3 collections
    # Note that there is no need to test setup_database() since it simply calls the first 3 methods we have below
    # Also note that there are no update operations in our code (since no object should be changed once added to db, but test can be added in if needed in the future)
    def test1_initialize_mongoDB_exercises_collection(self):
        """
        Test wger API calls and creation of exercise documents in the exercises collection for our remote mongoDB.
        1. Verifies there are at least 100 exercise documents stored
        2. Verifies every exercise document has a valid name, unique id, and in-order arrayIndex
        :return: None
        """
        # Invoke wger API to initialize the exercises collection in the test database
        main.initialize_mongoDB_exercises_collection(TestMain.TEST_DATABASE)
        ACTUAL_NUM_EXERCISE_DOCUMENTS = TestMain.TEST_DATABASE.exercises.estimated_document_count()
        EXPECTED_MIN_NUM_EXERCISE_DOCUMENTS = 100
        # 1.) Verify there are at least 100 exercise documents stored
        self.assertTrue(ACTUAL_NUM_EXERCISE_DOCUMENTS >= EXPECTED_MIN_NUM_EXERCISE_DOCUMENTS)
        # 2.) Verify every exercise document has a valid name, valid unique id, and a valid + in-order arrayIndex
        exercise_id_set = set()
        arrayIndexCounter = 0
        for exerciseDoc in TestMain.TEST_DATABASE.exercises.find():
            EXERCISE_NAME = exerciseDoc['name']
            EXERCISE_ID = exerciseDoc['id']
            EXERCISE_ARRAY_INDEX = exerciseDoc['arrayIndex']

            self.assertIsNotNone(EXERCISE_NAME)
            self.assertTrue(len(EXERCISE_NAME) > 0)
            self.assertIsNotNone(EXERCISE_ID)
            self.assertTrue(EXERCISE_ID not in exercise_id_set)
            exercise_id_set.add(EXERCISE_ID)
            self.assertIsNotNone(EXERCISE_ARRAY_INDEX)
            self.assertEqual(EXERCISE_ARRAY_INDEX, arrayIndexCounter)
            arrayIndexCounter += 1

    def test2_initialize_mongoDB_equipment_collection(self):
        """
        Test ebay API calls and creation of equipment documents in the equipments collection for our remote mongoDB.
        1. Verifies there are at least 40 equipment documents stored
        2. Verifies every equipment document has a valid name, unique id, and in-order arrayIndex
        :return: None
        """
        # Invoke ebay API to initialize the exercises collection in the test database
        main.initialize_mongoDB_equipment_collection(TestMain.TEST_DATABASE)
        ACTUAL_NUM_EQUIPMENT_DOCUMENTS = TestMain.TEST_DATABASE.equipments.estimated_document_count()
        EXPECTED_MIN_NUM_EQUIPMENT_DOCUMENTS = 40
        # 1.) Verify there are at least 40 equipment documents stored
        self.assertTrue(ACTUAL_NUM_EQUIPMENT_DOCUMENTS >= EXPECTED_MIN_NUM_EQUIPMENT_DOCUMENTS)
        # 2.) Verify every equipment document has a valid name, valid unique id, and a valid + in-order arrayIndex
        equipment_id_set = set()
        arrayIndexCounter = 0
        for equipmentDoc in TestMain.TEST_DATABASE.equipments.find():
            EQUIPMENT_NAME = equipmentDoc['name']
            EQUIPMENT_ID = equipmentDoc['id']
            EQUIPMENT_ARRAY_INDEX = equipmentDoc['arrayIndex']

            self.assertIsNotNone(EQUIPMENT_NAME)
            self.assertTrue(len(EQUIPMENT_NAME) > 0)
            self.assertIsNotNone(EQUIPMENT_ID)
            self.assertTrue(EQUIPMENT_ID not in equipment_id_set)
            equipment_id_set.add(EQUIPMENT_ID)
            self.assertIsNotNone(EQUIPMENT_ARRAY_INDEX)
            self.assertEqual(EQUIPMENT_ARRAY_INDEX, arrayIndexCounter)
            arrayIndexCounter += 1

    def test3_initialize_mongoDB_channel_collection(self):
        """
        Test Youtube API calls and creation of channel documents in the channels collection for our remote mongoDB.
        1. Verifies there are at least 40 channel documents stored
        2. Verifies every channel document has a valid name, unique id, and in-order arrayIndex
        :return: None
        """
        # Invoke Youtube API to initialize the channels collection in the test database
        main.initialize_mongoDB_channel_collection(TestMain.TEST_DATABASE)
        ACTUAL_NUM_CHANNEL_DOCUMENTS = TestMain.TEST_DATABASE.channels.estimated_document_count()
        EXPECTED_MIN_NUM_CHANNEL_DOCUMENTS = 40
        # 1.) Verify there are at least 40 channel documents stored
        self.assertTrue(ACTUAL_NUM_CHANNEL_DOCUMENTS >= EXPECTED_MIN_NUM_CHANNEL_DOCUMENTS)
        # 2.) Verify every channel document has a valid name, valid unique id, and a valid + in-order arrayIndex
        channel_id_set = set()
        arrayIndexCounter = 0
        for channelDoc in TestMain.TEST_DATABASE.channels.find():
            CHANNEL_NAME = channelDoc['name']
            CHANNEL_ID = channelDoc['id']
            CHANNEL_ARRAY_INDEX = channelDoc['arrayIndex']

            self.assertIsNotNone(CHANNEL_NAME)
            self.assertTrue(len(CHANNEL_NAME) > 0)
            self.assertIsNotNone(CHANNEL_ID)
            self.assertTrue(CHANNEL_ID not in channel_id_set)
            channel_id_set.add(CHANNEL_ID)
            self.assertIsNotNone(CHANNEL_ARRAY_INDEX)
            self.assertEqual(CHANNEL_ARRAY_INDEX, arrayIndexCounter)
            arrayIndexCounter += 1

    def test4_load_exercises_from_db(self):
        """
        Check that the exercises collection exists prior to testing the load_exercises_from_db() method,
        Then check each Exercise object in the returned exercise array
        :return: None
        """
        EXISTING_COLLECTIONS_BEFORE = TestMain.TEST_DATABASE.list_collection_names()
        if TestMain.EXERCISE_COLLECTION_NAME not in EXISTING_COLLECTIONS_BEFORE:
            print("test_phase2Database is missing the 'exercises' collection prior to loading test. Initializing now...")
            self.test_initialize_mongoDB_exercises_collection()

        # Call method from main.py to initialize the exerciseArray
        TEST_EXERCISE_ARRAY = main.load_exercises_from_db(TestMain.TEST_DATABASE)

        # Assert loaded exercise array has 100 or more objects
        self.assertTrue(len(TEST_EXERCISE_ARRAY) >= 100)

        # Assert each exercise object in the loaded exercise array has the following 3 properties
        for i in range(len(TEST_EXERCISE_ARRAY)):
            exercise_id_set = set()
            EXERCISE_OBJECT = TEST_EXERCISE_ARRAY[i]
            # 1.) Assert name is not None or empty
            self.assertIsNotNone(EXERCISE_OBJECT.name)
            self.assertTrue(len(EXERCISE_OBJECT.name) > 0)
            # 2.) Assert valid, unique id
            self.assertIsNotNone(EXERCISE_OBJECT.id)
            self.assertTrue(EXERCISE_OBJECT.id not in exercise_id_set)
            exercise_id_set.add(EXERCISE_OBJECT.id)
            # 3.) Assert arrayIndex is equal to the index position in the array
            self.assertEqual(EXERCISE_OBJECT.arrayIndex, i)

    def test5_load_equipments_from_db(self):
        """
        Check that the equipments collection exists prior to testing the load_equipments_from_db() method,
        Then verify each object in the returned equipment array
        :return: None
        """
        EXISTING_COLLECTIONS_BEFORE = TestMain.TEST_DATABASE.list_collection_names()
        if TestMain.EQUIPMENT_COLLECTION_NAME not in EXISTING_COLLECTIONS_BEFORE:
            print(f"test_phase2Database is missing the '{ TestMain.EQUIPMENT_COLLECTION_NAME }' collection prior to loading test. Initializing now...")
            self.test_initialize_mongoDB_equipment_collection()

        # Call method from main.py to initialize the equipment array
        TEST_EQUIPMENT_ARRAY = main.load_equipments_from_db(TestMain.TEST_DATABASE)

        # Assert loaded equipment array has 40 or more objects
        self.assertTrue(len(TEST_EQUIPMENT_ARRAY) >= 40)

        # Assert each equipment object in the loaded equipment array has the following 3 properties
        for i in range(len(TEST_EQUIPMENT_ARRAY)):
            equipment_id_set = set()
            EXERCISE_OBJECT = TEST_EQUIPMENT_ARRAY[i]
            # 1.) Assert name is not None or empty
            self.assertIsNotNone(EXERCISE_OBJECT.name)
            self.assertTrue(len(EXERCISE_OBJECT.name) > 0)
            # 2.) Assert valid, unique id
            self.assertIsNotNone(EXERCISE_OBJECT.id)
            self.assertTrue(EXERCISE_OBJECT.id not in equipment_id_set)
            equipment_id_set.add(EXERCISE_OBJECT.id)
            # 3.) Assert arrayIndex is equal to the index position in the array
            self.assertEqual(EXERCISE_OBJECT.arrayIndex, i)

    def test6_load_channels_from_db(self):
        """
        Check that the channels collection exists prior to testing the load_channels_from_db() method,
        Then check each channel object in the returned channel array
        :return: None
        """
        EXISTING_COLLECTIONS_BEFORE = TestMain.TEST_DATABASE.list_collection_names()
        if TestMain.CHANNEL_COLLECTION_NAME not in EXISTING_COLLECTIONS_BEFORE:
            print(f"test_phase2Database is missing the '{ TestMain.CHANNEL_COLLECTION_NAME }' collection prior to loading test. Initializing now...")
            self.test_initialize_mongoDB_channel_collection()

        # Call method from main.py to initialize the channels array
        TEST_CHANNEL_ARRAY = main.load_channels_from_db(TestMain.TEST_DATABASE)

        # Assert loaded channel array has 40 or more objects
        self.assertTrue(len(TEST_CHANNEL_ARRAY) >= 40)

        # Assert each Channel object in the loaded channel array has the following 3 properties
        for i in range(len(TEST_CHANNEL_ARRAY)):
            channel_id_set = set()
            CHANNEL_OBJECT = TEST_CHANNEL_ARRAY[i]
            # 1.) Assert name is not None or empty
            self.assertIsNotNone(CHANNEL_OBJECT.name)
            self.assertTrue(len(CHANNEL_OBJECT.name) > 0)
            # 2.) Assert valid, unique id
            self.assertIsNotNone(CHANNEL_OBJECT.id)
            self.assertTrue(CHANNEL_OBJECT.id not in channel_id_set)
            channel_id_set.add(CHANNEL_OBJECT.id)
            # 3.) Assert arrayIndex is equal to the index position in the array
            self.assertEqual(CHANNEL_OBJECT.arrayIndex, i)

    def test7_clean_database(self):
        """Assert that all 3 collections exist prior to this method, if so then verifies that dropping all 3 collections is successful
           in the remote mongoDB
        """
        EXISTING_COLLECTIONS_BEFORE = TestMain.TEST_DATABASE.list_collection_names()
        if TestMain.EXERCISE_COLLECTION_NAME not in EXISTING_COLLECTIONS_BEFORE:
            self.test_initialize_mongoDB_exercises_collection()
        if TestMain.EQUIPMENT_COLLECTION_NAME not in EXISTING_COLLECTIONS_BEFORE:
            self.test_initialize_mongoDB_equipment_collection()
        if TestMain.CHANNEL_COLLECTION_NAME not in EXISTING_COLLECTIONS_BEFORE:
            self.test_initialize_mongoDB_channel_collection()

        # Call method from main.py to drop all 3 collections
        main.clean_database(TestMain.TEST_DATABASE)

        # Verify all 3 collections have been dropped successfully
        EXISTING_COLLECTIONS_AFTER = TestMain.TEST_DATABASE.list_collection_names()
        self.assertTrue(TestMain.EXERCISE_COLLECTION_NAME not in EXISTING_COLLECTIONS_AFTER)
        self.assertTrue(TestMain.EQUIPMENT_COLLECTION_NAME not in EXISTING_COLLECTIONS_AFTER)
        self.assertTrue(TestMain.CHANNEL_COLLECTION_NAME not in EXISTING_COLLECTIONS_AFTER)


if __name__ == '__main__':
    unittest.main()
