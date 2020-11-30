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

<<<<<<< HEAD
=======
    # Helper functions for get_related_objects_for_instance functions
    @staticmethod
    def find_current_instance_object(id, currentCollection, keys):
        """
        Find the current instance object in the database and store important attributes
        """
        attributes = []
        currentDoc = currentCollection.find_one({'_id': id})

        if currentDoc:
            for key in keys:
                attributes.append(currentDoc[key])
        
        return attributes
>>>>>>> origin/dev

    @staticmethod
    def render_model_page(page_number, arr):
        pass

<<<<<<< HEAD

    @staticmethod
    def render_instance_page(instance_obj, related_objects):
        pass
        
=======
        return ModelInterface.find_related_objects(relatedCursor, ARRAY)

    @staticmethod
    def find_related_objects(relatedCursor, ARRAY):
        relatedInstances = []
        for relatedDoc in relatedCursor:
            relatedInstances.append(ARRAY[relatedDoc['arrayIndex']])
        return relatedInstances

    @staticmethod
    def paginate(page_number, array):
        """
        Pagination on Model Pages - assumes 9 instances per page
        """
        startIndex = (page_number - 1) * 9
        endIndex = (page_number * 9) - 1
        if endIndex >= len(array):
            endIndex = len(array) - 1
        num_pages = math.ceil(len(array) / 9)
        return startIndex, endIndex, num_pages
>>>>>>> origin/dev
