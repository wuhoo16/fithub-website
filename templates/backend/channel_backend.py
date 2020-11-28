from flask import render_template
from templates.backend.model_backend import ModelBackend
from templates.models.channel import Channel
import numpy as np

class ChannelBackend(ModelBackend, Channel):
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
    def load_from_db(db):
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
        
        ModelBackend.CHANNEL_ARRAY = channel_array


    @staticmethod
    def get_related_objects_for_instance(id, db):
        attributes = ModelBackend.find_current_instance_object(id, db.channels, ('exerciseCategory', 'exerciseSubcategory'))
        category = attributes[0]
        subcategory = attributes[1]

        relatedExercises = ModelBackend.find_related_objects_based_on_subcategory(subcategory, db.exercises, ['category', category], ['subcategory', subcategory], ModelBackend.EXERCISES_ARRAY)

        # Use the first related exercise object to determine what equipmentCategory to use when querying equipments collection
        topExerciseDoc = db.exercises.find_one({'_id': relatedExercises[0].id})
        if topExerciseDoc:
            equipmentCategory = topExerciseDoc['equipment'][0]  # Select the first equipment term in the equipment array attribute to use

        relatedEquipments = ModelBackend.find_related_objects(db.equipments.find({'equipmentCategory': equipmentCategory}), ModelBackend.EQUIPMENT_ARRAY)
        relatedChannels = ModelBackend.find_related_objects_based_on_subcategory(subcategory, db.channels, ['exerciseCategory', category], ['exerciseSubcategory', subcategory], ModelBackend.CHANNEL_ARRAY)

        return [relatedExercises, relatedEquipments, relatedChannels]

        
    @staticmethod
    def filter(db, requestForm):
        # Setting up to filter
        selectedSubscriberRange = requestForm.getlist("checkedSubscriberRange")
        selectedTotalViewsRange = requestForm.getlist("checkedTotalViewsRange")
        selectedVideosRange = requestForm.getlist("checkedVideosRange")
        #NOTE checked was selected -- make sure it works

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
            filteredChannels = np.array(ModelBackend.find_related_objects(db.channels.find({'subscriberCount': {'$gte': int(subscriberRangeList[0]), '$lt': int(subscriberRangeList[1])}}), ModelBackend.CHANNEL_ARRAY))

        # Query the entire exercises collection on selected ranges and append matching Exercise objects
        for totalViewsString in selectedTotalViewsRange:
            totalViewsList = totalViewsString.split(" ")
            filteredChannels = np.append(filteredChannels, np.array(ModelBackend.find_related_objects(db.channels.find({'viewCount': {'$gte': int(totalViewsList[0]), '$lt': int(totalViewsList[1])}}), ModelBackend.CHANNEL_ARRAY)))

        # Query the entire exercises collection on each of the selected ranges and append matching Exercise objects
        for videoRangeString in selectedVideosRange:
            videoRangeList = videoRangeString.split(" ")
            filteredChannels = np.append(filteredChannels, np.array(ModelBackend.find_related_objects(db.channels.find({'videoCount': {'$gte': int(videoRangeList[0]), '$lt': int(videoRangeList[1])}}), ModelBackend.CHANNEL_ARRAY)))

        # Return all of filtered Exercise objects
        return tempModifiedArray, filteredChannels


    @staticmethod
    def render_model_page(page_number, arr):
        start, end, num_pages = ModelBackend.paginate(page_number, arr)
        return render_template('channels.html', channelArray=arr, start=start, end=end, page_number=page_number, num_pages=num_pages)


    @staticmethod
    def render_instance_page(instance_obj, related_objects):
        return render_template('channelInstance.html', channelObj=instance_obj, relatedObjects=related_objects)
