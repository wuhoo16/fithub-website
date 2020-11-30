from abc import ABC
from templates.backend.model_interface import ModelBackendInterface
import math

class ModelBackend(ModelBackendInterface, ABC):
    # All are initialized from our mongoDB the first time the homepage is visited
    EXERCISES_ARRAY = []
    EQUIPMENT_ARRAY = []
    CHANNEL_ARRAY = []

    @staticmethod
    def load_and_return_model_array_from_db(db):
        pass

    @staticmethod
    def get_related_objects_for_instance(id, db):
        pass

    @staticmethod
    def filter(page_number, arr):
        pass

    @staticmethod
    def render_model_page(page_number, arr):
        pass

    @staticmethod
    def render_instance_page(instance_obj, related_objects):
        pass


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

    @staticmethod
    def find_related_objects_based_on_subcategory(subcategory, collection, invalid_input, valid_input, arr):
        """
        Query a collection for all instances that match current exerciseCategory/Subcategory based on if the subcategory is None
        """
        if subcategory is None:
            relatedCursor = collection.find({invalid_input[0]: invalid_input[1]})
        else: # exerciseSubcategory is not None
            relatedCursor = collection.find({valid_input[0]: valid_input[1]})

        return self.find_related_objects(relatedCursor, arr)
    
    @staticmethod
    def find_related_objects(relatedCursor, arr):
        relatedInstances = []
        for relatedDoc in relatedCursor:
            relatedInstances.append(arr[relatedDoc['arrayIndex']])
        return relatedInstances

    @staticmethod
    def paginate(pageNumber, currentArray):
        """
        Pagination on Model Pages - assumes 9 instances per page
        """
        startIndex = (pageNumber - 1) * 9
        endIndex = (pageNumber * 9) - 1
        if endIndex >= len(currentArray):
            endIndex = len(currentArray) - 1
        numPages = math.ceil(len(currentArray) / 9)
        return startIndex, endIndex, numPages
