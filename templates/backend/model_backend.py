from abc import ABC, abstractmethod
from templates.backend.model_interface import ModelBackendInterface
import math


# Concrete superclass of all 3 model backend classes to pull out shared code among all models such as...
# 1.) Finding the current object and related cross-model instances
# 2.) Pagination if given the current selected page number and currentArray of objects
class ModelBackend(ModelBackendInterface, ABC):
    # All are initialized from our mongoDB the first time the homepage is visited
    EXERCISES_ARRAY = []
    EQUIPMENT_ARRAY = []
    CHANNEL_ARRAY = []

    @staticmethod
    @abstractmethod
    def load_and_return_model_array_from_db(db):
        pass

    @staticmethod
    @abstractmethod
    def get_related_objects_for_instance(id, db):
        pass

    @staticmethod
    @abstractmethod
    def filter(page_number, arr):
        pass

    @staticmethod
    @abstractmethod
    def render_model_page(page_number, arr):
        pass

    @staticmethod
    @abstractmethod
    def render_instance_page(instance_obj, related_objects):
        pass

    # Defined helper functions of all shared code definition among the 3 model type backend classes
    # Includes querying the mondoDB for finding related objects as well as pagination logic
    # ===================================================================================================
    @staticmethod
    def get_current_instance_object_attributes(id, currentCollection, keys):
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

        return ModelBackend.find_related_objects(relatedCursor, arr, arr)

    # TODO: WE SHOULD SEPARATE THIS FUNCTION TO THE TWO DIFFERENT STATIC METHODS THAT ARE USED BY <modelType>_BACKEND filter() vs. get_related_object_for_instance... They have different parameter requirements
    # since filtering needs a third parameter of the globalArray to correct handle logic of querying the mongoDB while getting related objects ALWAYS passed in the globalArray (it also has more complex logic to prevent
    # array out of bounds error)
    @staticmethod
    def find_related_objects(relatedCursor, currentArray, globalArray):
        relatedInstances = []

        # Only allow database results if it is contained in the passed array (may be a subset of the collection)
        validArrayIndexSet = set()
        for obj in currentArray:
            validArrayIndexSet.add(obj.arrayIndex)

        for relatedDoc in relatedCursor:
            if relatedDoc['arrayIndex'] in validArrayIndexSet:
                relatedInstances.append(globalArray[relatedDoc['arrayIndex']])
        return list(set(relatedInstances))

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
