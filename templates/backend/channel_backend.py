from flask import render_template
from templates.backend.model_backend import ModelBackend
from templates.models.channel import Channel
import numpy as np


class ChannelBackend(ModelBackend, Channel):
    searchItemsKey = 'channelsSearchItems'
    sortingHiddenFieldKey = 'channelsSortingHiddenField'
    sortCriteriaMenuKey = 'channelsSortCriteriaMenu'

    @staticmethod
    def load_and_return_model_array_from_db(db):
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
        # Refactor this later, but try to ensure ModelBackend global arrays are intialized for now
        ModelBackend.CHANNEL_ARRAY = channel_array
        return channel_array

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

        relatedEquipments = ModelBackend.find_related_objects(db.equipments.find({'equipmentCategory': equipmentCategory}), ModelBackend.EQUIPMENT_ARRAY, ModelBackend.EQUIPMENT_ARRAY)
        relatedChannels = ModelBackend.find_related_objects_based_on_subcategory(subcategory, db.channels, ['exerciseCategory', category], ['exerciseSubcategory', subcategory], ModelBackend.CHANNEL_ARRAY)

        return [relatedExercises, relatedEquipments, relatedChannels]

    @staticmethod
    def filter(db, filterRequestForm, currentArray):
        # Setting up to filter
        selectedSubscriberRange = filterRequestForm.getlist("checkedSubscriberRange")
        selectedTotalViewsRange = filterRequestForm.getlist("checkedTotalViewsRange")
        selectedVideosRange = filterRequestForm.getlist("checkedVideosRange")

        # Query the entire exercises collection on all selected ranges and append matching Exercise objects
        filteredChannels = []
        for subscriberRangeString in selectedSubscriberRange:
            subscriberRangeList = subscriberRangeString.split(" ")
            filteredChannels += ModelBackend.find_related_objects(db.channels.find({'subscriberCount': {'$gte': int(subscriberRangeList[0]), '$lt': int(subscriberRangeList[1])}}), currentArray, ModelBackend.CHANNEL_ARRAY)

        # Query the entire exercises collection on selected ranges and append matching Exercise objects
        # UNION OF PREVIOUS FILTER RESULTS
        for totalViewsString in selectedTotalViewsRange:
            totalViewsList = totalViewsString.split(" ")
            filteredChannels += ModelBackend.find_related_objects(db.channels.find({'viewCount': {'$gte': int(totalViewsList[0]), '$lt': int(totalViewsList[1])}}), currentArray, ModelBackend.CHANNEL_ARRAY)

        # Query the entire exercises collection on each of the selected ranges and append matching Exercise objects
        # UNION OF PREVIOUS FILTER RESULTS
        for videoRangeString in selectedVideosRange:
            videoRangeList = videoRangeString.split(" ")
            filteredChannels += ModelBackend.find_related_objects(db.channels.find({'videoCount': {'$gte': int(videoRangeList[0]), '$lt': int(videoRangeList[1])}}), currentArray, ModelBackend.CHANNEL_ARRAY)

        # Return all of filtered Exercise objects
        return list(set(filteredChannels))

    @staticmethod
    def render_model_page(pageNumber, currentArray, resetLocalStorageFlag):
        print(f'Before pagination, the currentArray is: {currentArray}')
        start, end, numPages = ModelBackend.paginate(pageNumber, currentArray)
        print(f'After pagination, the currentArray is: {currentArray}')
        return render_template('channels.html',
                               currentChannelArray=currentArray,
                               start=start,
                               end=end,
                               pageNumber=pageNumber,
                               numPages=numPages,
                               resetLocalStorageFlag=resetLocalStorageFlag)

    @staticmethod
    def render_instance_page(instance_obj, related_objects):
        return render_template('channelInstance.html', channelObj=instance_obj, relatedObjects=related_objects)
