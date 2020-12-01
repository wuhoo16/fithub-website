from abc import ABC
from flask import render_template

from templates.backend.model_interface import ModelBackendInterface
import math


# Concrete superclass of all 3 model backend classes to pull out shared code among all models such as...
# 1.) Finding the current object attributes in the mongoDB
# 2.) Pagination if given the current selected page number and currentArray of objects
class ModelBackend(ModelBackendInterface, ABC):
    @staticmethod
    def render_model_page(pageNumber, currentArray, resetLocalStorageFlag, modelType):
        MODEL_HTML_FILE_NAME = '{}s.html'
        start, end, numPages = ModelBackend.paginate(pageNumber, currentArray)
        return render_template(MODEL_HTML_FILE_NAME.format(modelType),
                               currentArray=currentArray,
                               start=start,
                               end=end,
                               pageNumber=pageNumber,
                               numPages=numPages,
                               resetLocalStorageFlag=resetLocalStorageFlag)

    @staticmethod
    def render_instance_page(instanceObject, relatedObjects, modelType):
        # The modelType param should be one of the following strings: 'exercise', 'equipment', 'channel'
        if modelType != 'exercise' and modelType != 'equipment' and modelType != 'channel':
            raise NameError(
                f"Caught error before rendering the instance page! Passed in modelType={modelType} but must be a string equal to 'exercise', 'equipment', or 'channel'")
        INSTANCE_HTML_FILE_NAME = '{}Instance.html'
        return render_template(INSTANCE_HTML_FILE_NAME.format(modelType), instanceObject=instanceObject,
                               relatedObjects=relatedObjects)

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
    def find_related_objects_based_on_subcategory(subcategory, collection, invalid_input, valid_input, globalArray):
        """
        Query a collection for all instances that match current exerciseCategory/Subcategory based on if the subcategory is None
        """
        if subcategory is None:
            relatedCursor = collection.find({invalid_input[0]: invalid_input[1]})
        else:  # exerciseSubcategory is not None
            relatedCursor = collection.find({valid_input[0]: valid_input[1]})

        return ModelBackend.find_related_objects(relatedCursor, globalArray)

    @staticmethod
    def find_related_objects(relatedCursor, globalArray):
        relatedInstances = []

        for relatedDoc in relatedCursor:
            relatedInstances.append(globalArray[relatedDoc['arrayIndex']])
        return relatedInstances

    @staticmethod
    def find_related_objects_for_filter_operation(relatedCursor, currentArray, globalArray):
        relatedInstances = []

        # Only allow database results if it is contained in the passed array (may be a subset of the collection)
        validArrayIndexSet = set()
        for obj in currentArray:
            validArrayIndexSet.add(obj.arrayIndex)

        for relatedDoc in relatedCursor:
            if relatedDoc['arrayIndex'] in validArrayIndexSet:
                relatedInstances.append(globalArray[relatedDoc['arrayIndex']])
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
