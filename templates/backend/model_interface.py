import math
from abc import ABC, abstractmethod


# Note that ModelInterface is an abstract base class = Python's version of an interface
class ModelBackendInterface(ABC):
    # All are initialized from our mongoDB the first time the homepage is visited
    EXERCISES_ARRAY = []
    EQUIPMENT_ARRAY = []
    CHANNEL_ARRAY = []

    @staticmethod
    @abstractmethod
    def initialize_array_from_mongo_database(db):
        """
        Method for loading from the remote MongoDB to initialize model global array
        NOTE THAT ANY CHANGES TO THE OBJECT CONSTRUCTORS MUST BE CHANGED HERE TO MATCH!
        """
        pass
    
    @staticmethod
    @abstractmethod
    def get_related_objects_for_instance(id, db):
        """
        Getting 2D list of related cross-model objects by using the arrayIndex attribute
        :param id: The current channel instance object's id attribute
        :param db: The mongo database to query from
        :return: a 2D list of lists containing all the related instance ids for all 3 model types

        By passing the id value of any instance, each method will return a Python list in the format: [[], [], []] where
        <returnedList>[0] will be the list containing all of the related EXERCISE instance objects
        <returnedList>[1] will be the list containing all of the related EQUIPMENT instance objects
        <returnedList>[2] will be the list containing all of the related CHANNEL instance objects
        NOTE THAT WE CURRENTLY USE AN INDIRECT METHOD TO FIND ALL RELATED EQUIPMENT. Result relevance may vary...
        ====================================================================================================================
        """
        pass

    @staticmethod
    @abstractmethod
    def filter(db, **kwargs):
        """
        Pass in the selected categories to filter on and return all of the filtered model objects in a Python list.
        :param db: The remote mongoDB to query
        :param **kwargs: parameter to be filtered by
        :return: a list containing all of the filtered model objects

        Helper method for filtering mongoDB collection given lists of user-selected categories from the HTML form
        """
        pass

    @staticmethod
    def render_model_page(page_number, arr):
        pass

    @staticmethod
    def render_instance_page(instance_obj, related_objects):
        pass
        
