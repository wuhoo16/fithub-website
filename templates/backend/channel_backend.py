from flask import render_template
from templates.backend.model_interface import ModelInterface
from templates.channel import Channel
import numpy as np


class ChannelBackend(ModelInterface, Channel):
    filterIsActive = False
    searchIsActive = False
    sortIsActive = False
    sortingAttribute = ""
    sortingDirection = ""

    searchItemsKey = 'channelsSearchItems'
    sortingHiddenFieldKey = 'channelsSortingHiddenField'
    sortCriteriaMenuKey = 'channelsSortCriteriaMenu'

    modifiedArray = []

    @staticmethod
    def reset_all_flags():
        ChannelBackend.filterIsActive = False
        ChannelBackend.sortIsActive = False
        ChannelBackend.searchIsActive = False

    @staticmethod
    def initialize_array_from_mongo_database(db):
        channel_array = []
        channelCursor = db.channels.find()
        for channelDocument in channelCursor:
            channel_array.append(Channel(**{
                "id": channelDocument['id'],
                "arrayIndex": channelDocument['arrayIndex'],
                "name": channelDocument['name'],
                "description": channelDocument['description'],
                "thumbnailURL": channelDocument['thumbnailURL'],
                "subscriberCount": channelDocument['subscriberCount'],
                "viewCount": channelDocument['viewCount'],
                "videoCount": channelDocument['videoCount'],
                "playlist": channelDocument['playlist'],
                "topicIdCategories": channelDocument['topicIdCategories'],
                "exerciseCategory": channelDocument['exerciseCategory'],
                "unsubscribedTrailer": channelDocument['unsubscribedTrailer'],
                "bannerUrl": channelDocument['bannerUrl'],
                "keywords": channelDocument['keywords'],
                "exerciseSubcategory": channelDocument['exerciseSubcategory']
            }))
        
        ModelInterface.CHANNEL_ARRAY = channel_array

    @staticmethod
    def get_related_objects_for_instance(id, db):
        attributes = ModelInterface.find_current_instance_object(id, db.channels, ('exerciseCategory', 'exerciseSubcategory'))
        category = attributes[0]
        subcategory = attributes[1]

        relatedExercises = ModelInterface.find_related_objects_based_on_subcategory(subcategory, db.exercises, ['category', category], ['subcategory', subcategory], ModelInterface.EXERCISES_ARRAY)

        # Use the first related exercise object to determine what equipmentCategory to use when querying equipments collection
        topExerciseDoc = db.exercises.find_one({'_id': relatedExercises[0].id})
        if topExerciseDoc:
            equipmentCategory = topExerciseDoc['equipment'][0]  # Select the first equipment term in the equipment array attribute to use

        relatedEquipments = ModelInterface.find_related_objects(db.equipments.find({'equipmentCategory': equipmentCategory}), ModelInterface.EQUIPMENT_ARRAY)
        relatedChannels = ModelInterface.find_related_objects_based_on_subcategory(subcategory, db.channels, ['exerciseCategory', category], ['exerciseSubcategory', subcategory], ModelInterface.CHANNEL_ARRAY)

        return [relatedExercises, relatedEquipments, relatedChannels]

    @staticmethod
    def filter(db, requestForm):
        # Setting up to filter
        selectedSubscriberRange = requestForm.getlist("checkedSubscriberRange")
        selectedTotalViewsRange = requestForm.getlist("checkedTotalViewsRange")
        selectedVideosRange = requestForm.getlist("checkedVideosRange")
        # NOTE checked was selected -- make sure it works

        if len(selectedSubscriberRange) == 0 and len(selectedTotalViewsRange) == 0 and len(selectedVideosRange) == 0:
            ChannelBackend.searchIsActive = True
        
        tempModifiedArray = []
        if ChannelBackend.searchIsActive:
            tempModifiedArray = ChannelBackend.modifiedArray

        # Beginning to implement filter
        filteredChannels = []

        # Query the entire exercises collection on all selected ranges and append matching Exercise objects
        for subscriberRangeString in selectedSubscriberRange:
            subscriberRangeList = subscriberRangeString.split(" ")
            filteredChannels = np.array(ModelInterface.find_related_objects(db.channels.find({'subscriberCount': {'$gte': int(subscriberRangeList[0]), '$lt': int(subscriberRangeList[1])}}), ModelInterface.CHANNEL_ARRAY))

        # Query the entire exercises collection on selected ranges and append matching Exercise objects
        for totalViewsString in selectedTotalViewsRange:
            totalViewsList = totalViewsString.split(" ")
            filteredChannels = np.append(filteredChannels, np.array(ModelInterface.find_related_objects(db.channels.find({'viewCount': {'$gte': int(totalViewsList[0]), '$lt': int(totalViewsList[1])}}), ModelInterface.CHANNEL_ARRAY)))

        # Query the entire exercises collection on each of the selected ranges and append matching Exercise objects
        for videoRangeString in selectedVideosRange:
            videoRangeList = videoRangeString.split(" ")
            filteredChannels = np.append(filteredChannels, np.array(ModelInterface.find_related_objects(db.channels.find({'videoCount': {'$gte': int(videoRangeList[0]), '$lt': int(videoRangeList[1])}}), ModelInterface.CHANNEL_ARRAY)))

        # Return all of filtered Exercise objects
        return tempModifiedArray, filteredChannels

    @staticmethod
    def render_model_page(page_number, ARR):
        start, end, num_pages = ModelInterface.paginate(page_number, ARR)
        return render_template('channels.html', channelArray=ARR, start=start, end=end, page_number=page_number, num_pages=num_pages)

    @staticmethod
    def render_instance_page(instanceObj, relatedObjects):
        return render_template('channelInstance.html', channelObj=instanceObj, relatedObjects=relatedObjects)
