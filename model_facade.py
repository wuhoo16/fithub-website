from templates.api.exercise_api import ExerciseAPI
from templates.api.equipment_api import EquipmentAPI
from templates.api.channel_api import ChannelAPI
from templates.backend.model_backend import ModelBackend

from flask import render_template

from templates.models.channel import Channel
from templates.models.equipment import Equipment
from templates.models.exercise import Exercise


class ModelFacade:
    # Parameterized Constructor
    # ==========================================
    def __init__(self, db):
        self.EXERCISES_ARRAY = None
        self.EQUIPMENT_ARRAY = None
        self.CHANNEL_ARRAY = None
        self.db = db
        self.searchItemsKeyTemplate = '{}sSearchItems'
        self.sortingHiddenFieldKeyTemplate = '{}sSortingHiddenField'
        self.sortCriteriaMenuKeyTemplate = '{}sSortCriteriaMenu'
        self.__initialize_model_arrays()

    # Getter methods
    # =========================================
    def get_exercises_array(self):
        print(f'In the get function, the EXERCISES_ARRAY= {self.EXERCISES_ARRAY}')
        return self.EXERCISES_ARRAY

    def get_equipment_array(self):
        return self.EQUIPMENT_ARRAY

    def get_channel_array(self):
        return self.CHANNEL_ARRAY

    # MongoDB remote database is defined below including:
    # ======================================================================================================
    def setup_database(self, modelType=None):
        """
        Setup the remote mongoDB by initializing all the model collections passed into args argument. Note that if the 2nd parameter
        is not provided, this method will initialize all 3 collections by default.
        :param modelType: Optional parameter to only initialize one model collection. Expects one of the following strings: 'exercises', 'equipments', 'channels'
        :return: None
        """
        if modelType is None:
            ExerciseAPI.initialize_mongoDB_collection(self.db)
            EquipmentAPI.initialize_mongoDB_collection(self.db)
            ChannelAPI.initialize_mongoDB_collection(self.db)
        else:
            if modelType == "exercises":
                ExerciseAPI.initialize_mongoDB_collection(self.db)
            elif modelType == "equipments":
                EquipmentAPI.initialize_mongoDB_collection(self.db)
            elif modelType == "channels":
                ChannelAPI.initialize_mongoDB_collection(self.db)
            else:
                raise NameError("ERROR: " + modelType + " is not a valid model type! "
                                                        "Only 'exercises', 'equipments', or 'channels' are supported parameters to pass in.")

    def clean_database(self):
        """
        Cleans the current phase's database by dropping all 3 model collections.
        :return: None
        """
        self.db.exercises.drop()
        self.db.equipments.drop()
        self.db.channels.drop()

    def get_exercises_array_from_db(self):
        """
        Return a python list of all Exercise objects.
        :return: A python list of Exercise objects
        """
        exercise_array = []
        exercisesCursor = self.db.exercises.find()
        for exerciseDocument in exercisesCursor:
            exercise_array.append(
                Exercise(**{
                    "exercise_id": exerciseDocument['id'],
                    "arrayIndex": exerciseDocument['arrayIndex'],
                    "name": exerciseDocument['name'],
                    "description": exerciseDocument['description'],
                    "category": exerciseDocument['category'],
                    "subcategory": exerciseDocument['subcategory'],
                    "muscles": exerciseDocument['muscles'],
                    "muscles_secondary": exerciseDocument['muscles_secondary'],
                    "equipment": exerciseDocument['equipment'],
                    "images": exerciseDocument['images'],
                    "comments": exerciseDocument['comments']
                }))
        return exercise_array

    def get_equipment_array_from_db(self):
        """
        Return a python list of all Equipment objects.
        :return: A python list of Equipment objects
        """
        equipment_array = []
        equipmentsCursor = self.db.equipments.find()
        for equipmentDocument in equipmentsCursor:
            equipment_array.append(Equipment(**{
                "itemId": equipmentDocument['id'],
                "arrayIndex": equipmentDocument['arrayIndex'],
                "title": equipmentDocument['name'],
                "value": equipmentDocument['price'],
                "categoryName": equipmentDocument['category'],
                "location": equipmentDocument['location'],
                "replacePictureFlag": equipmentDocument['replacePictureFlag'],
                "galleryURL": equipmentDocument['picture'],
                "viewItemURL": equipmentDocument['linkToItem'],
                "equipmentCategory": equipmentDocument['equipmentCategory']
            }))
        return equipment_array

    def get_channel_array_from_db(self):
        channel_array = []
        channelCursor = self.db.channels.find()
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
        return channel_array

    # ALL RENDER METHODS FOR FLASK VIEW METHODS BELOW
    # ======================================================================================================
    @staticmethod
    def render_homepage():
        return render_template('homepage.html')

    @staticmethod
    def render_about_page():
        return render_template('about.html')

    def render_model_page(self, modelType, pageNumber, flaskRequest, currentArray, operationUsed):
        if modelType != 'exercise' and modelType != 'equipment' and modelType != 'channel':
            raise NameError("ERROR: " + modelType + " is not a supported model type!")

        # Convert currentArray to array of objects if it is current an array of indices, else just retain array
        currentArray = self.__get_object_array_from_current_array(modelType, currentArray)

        if flaskRequest.method == 'POST':
            if operationUsed == "Filter":
                return self.__handle_filter_operation(modelType, flaskRequest, currentArray, pageNumber)
            elif operationUsed == "Sort":
                return self.__handle_sort_operation(modelType, flaskRequest, currentArray, pageNumber)
            elif operationUsed == "Search":
                return self.__handle_search_operation(modelType, flaskRequest, currentArray, pageNumber)
            else:
                raise NameError(
                    f"operationUsed={operationUsed} is not valid! Must be either 'Search', 'Sort', or 'Filter' for a POST request!")
        elif flaskRequest.method == 'GET':
            if operationUsed == "Pagination":
                return ModelBackend.render_model_page(pageNumber, currentArray, 0, modelType)
            else:
                return ModelBackend.render_model_page(pageNumber, currentArray, 1, modelType)
        else:  # Not a POST or GET request
            raise NameError("Not a supported Flask request. Only GET and POST requests are supported!")

    def render_instance_page(self, modelType, array_index):
        if modelType != 'exercise' and modelType != 'equipment' and modelType != 'channel':
            raise NameError("ERROR: " + modelType + " is not a supported model type!")

        instanceObject = None
        if modelType == 'exercise':
            instanceObject = self.EXERCISES_ARRAY[array_index]
        elif modelType == 'equipment':
            instanceObject = self.EQUIPMENT_ARRAY[array_index]
        elif modelType == 'channel':
            instanceObject = self.CHANNEL_ARRAY[array_index]
        relatedObjects = self.__get_related_cross_model_objects(modelType, instanceObject.id)
        return ModelBackend.render_instance_page(instanceObject, relatedObjects, modelType)

    # Private helper methods used internally in the ModelFacade class
    # ======================================================================================================
    def __initialize_model_arrays(self):
        self.EXERCISES_ARRAY = self.get_exercises_array_from_db()
        self.EQUIPMENT_ARRAY = self.get_equipment_array_from_db()
        self.CHANNEL_ARRAY = self.get_channel_array_from_db()

    def __get_object_array_from_current_array(self, modelType, currentArray):
        if len(currentArray) != 0:
            if isinstance(currentArray[0], int):
                currentArrayOfObjects = []
                for arrayIndex in currentArray:
                    if modelType == 'exercise':
                        currentArrayOfObjects.append(self.EXERCISES_ARRAY[arrayIndex])
                    elif modelType == 'equipment':
                        currentArrayOfObjects.append(self.EQUIPMENT_ARRAY[arrayIndex])
                    elif modelType == 'channel':
                        currentArrayOfObjects.append(self.CHANNEL_ARRAY[arrayIndex])
                return currentArrayOfObjects
            else:  # currentArray already contains objects
                return currentArray
        else:
            return []

    def __get_filtered_exercises(self, filterRequestForm, currentArray):
        # setting up to filter
        selectedExerciseCategories = filterRequestForm.getlist("checkedExerciseCategories")
        selectedEquipmentCategories = filterRequestForm.getlist("checkedEquipmentCategories")

        # Query the entire exercises collection on each of the selected exercise category terms and append matching Exercise objects
        filteredExercises = []
        for exerciseCategory in selectedExerciseCategories:
            filteredExercises += ModelBackend.find_related_objects_for_filter_operation(
                self.db.exercises.find({'category': exerciseCategory}), currentArray, self.EXERCISES_ARRAY)

        # Query the entire exercises collection on each of the selected equipment category terms and append matching Exercise objects
        # NOTE THAT WE ARE TAKING THE UNION OF SELECTED FILTERING CHECKBOXES NOT THE INTERSECTION
        for equipmentCategory in selectedEquipmentCategories:
            filteredExercises += ModelBackend.find_related_objects_for_filter_operation(
                self.db.exercises.find({'equipment': equipmentCategory}), currentArray, self.EXERCISES_ARRAY)

        # Return all of matching Exercise objects after filtering on the currentArray
        return list(set(filteredExercises))

    def __get_filtered_equipments(self, filterRequestForm, currentArray):
        # Setting up for filtering
        selectedPriceRanges = filterRequestForm.getlist("checkedPriceRange")
        selectedEquipmentCategories = filterRequestForm.getlist("checkedEquipmentCategories")

        # Query the entire exercises collection on each of the selected exercise category terms and append matching objects with matching price ranges
        filteredEquipments = []
        for priceString in selectedPriceRanges:
            priceRangeList = priceString.split(" ")
            filteredEquipments += ModelBackend.find_related_objects_for_filter_operation(
                self.db.equipments.find({'price': {'$gte': float(priceRangeList[0]), '$lt': float(priceRangeList[1])}}),
                currentArray, self.EQUIPMENT_ARRAY)

        # Query the entire exercises collection on each of the selected equipment category terms and add the Exercise objects with matching equipment categories
        # NOTE THAT WE ARE TAKING THE UNION OF SELECTED FILTERING CHECKBOXES NOT THE INTERSECTION
        for equipmentCategory in selectedEquipmentCategories:
            filteredEquipments += ModelBackend.find_related_objects_for_filter_operation(
                self.db.equipments.find({'equipmentCategory': equipmentCategory}), currentArray, self.EQUIPMENT_ARRAY)

        # Return all of filtered Exercise objects
        return list(set(filteredEquipments))

    def __get_filtered_channels(self, filterRequestForm, currentArray):
        # Setting up to filter
        selectedSubscriberRange = filterRequestForm.getlist("checkedSubscriberRange")
        selectedTotalViewsRange = filterRequestForm.getlist("checkedTotalViewsRange")
        selectedVideosRange = filterRequestForm.getlist("checkedVideosRange")

        # Query the entire exercises collection on all selected ranges and append matching Exercise objects
        filteredChannels = []
        for subscriberRangeString in selectedSubscriberRange:
            subscriberRangeList = subscriberRangeString.split(" ")
            filteredChannels += ModelBackend.find_related_objects_for_filter_operation(self.db.channels.find(
                {'subscriberCount': {'$gte': int(subscriberRangeList[0]), '$lt': int(subscriberRangeList[1])}}),
                                                                  currentArray, self.CHANNEL_ARRAY)

        # Query the entire exercises collection on selected ranges and append matching Exercise objects
        # UNION OF PREVIOUS FILTER RESULTS
        for totalViewsString in selectedTotalViewsRange:
            totalViewsList = totalViewsString.split(" ")
            filteredChannels += ModelBackend.find_related_objects_for_filter_operation(
                self.db.channels.find({'viewCount': {'$gte': int(totalViewsList[0]), '$lt': int(totalViewsList[1])}}),
                currentArray, self.CHANNEL_ARRAY)

        # Query the entire exercises collection on each of the selected ranges and append matching Exercise objects
        # UNION OF PREVIOUS FILTER RESULTS
        for videoRangeString in selectedVideosRange:
            videoRangeList = videoRangeString.split(" ")
            filteredChannels += ModelBackend.find_related_objects_for_filter_operation(
                self.db.channels.find({'videoCount': {'$gte': int(videoRangeList[0]), '$lt': int(videoRangeList[1])}}),
                currentArray, self.CHANNEL_ARRAY)

        # Return all of filtered Exercise objects
        return list(set(filteredChannels))

    def __get_related_cross_model_objects(self, modelType, instanceObjectID):
        print('In the __get_related_cross_model_objects method()...')
        # At this point modelType has already been checked to be one of these cases
        if modelType == 'exercise':
            related_2D_array = self.__get_related_objects_for_exercise_instance(instanceObjectID)
            print(f'2D array related to exercise instance is: {related_2D_array}')
            return related_2D_array
        elif modelType == 'equipment':
            related_2D_array = self.__get_related_objects_for_equipment_instance(instanceObjectID)
            print(f'2D array related to equipment instance is: {related_2D_array}')
            return related_2D_array
        elif modelType == 'channel':
            related_2D_array = self.__get_related_objects_for_channel_instance(instanceObjectID)
            return self.__get_related_objects_for_channel_instance(instanceObjectID)
            return related_2D_array

    def __get_related_objects_for_exercise_instance(self, id):
        attributes = ModelBackend.get_current_instance_object_attributes(id, self.db.exercises,
                                                                         ('category', 'subcategory', 'equipment'))
        category = attributes[0]
        subcategory = attributes[1]
        equipmentCategoryList = attributes[2]

        relatedExercises = ModelBackend.find_related_objects_based_on_subcategory(subcategory, self.db.exercises,
                                                                                  ['category', category],
                                                                                  ['subcategory', subcategory],
                                                                                  self.EXERCISES_ARRAY)
        relatedEquipments = []
        for equipmentCategory in equipmentCategoryList:
            relatedEquipments += ModelBackend.find_related_objects(
                self.db.equipments.find({'equipmentCategory': equipmentCategory}), self.EQUIPMENT_ARRAY)

        relatedChannels = ModelBackend.find_related_objects_based_on_subcategory(subcategory, self.db.channels,
                                                                                 ['exerciseCategory', category],
                                                                                 ['exerciseSubcategory', subcategory],
                                                                                 self.CHANNEL_ARRAY)

        return [relatedExercises, relatedEquipments, relatedChannels]

    def __get_related_objects_for_equipment_instance(self, id):
        attributes = ModelBackend.get_current_instance_object_attributes(id, self.db.equipments, ['equipmentCategory'])
        equipmentCategory = attributes[0]

        relatedExercises = ModelBackend.find_related_objects(self.db.exercises.find({'equipment': equipmentCategory}),
                                                             self.EXERCISES_ARRAY)

        # Use the first related exercise object to determine what exercise category/subcategory to use when querying channels collection
        topExerciseDoc = self.db.exercises.find_one({'_id': relatedExercises[0].id})
        if topExerciseDoc:
            exerciseCategory = topExerciseDoc['category']
            exerciseSubcategory = topExerciseDoc['subcategory']

        relatedEquipments = ModelBackend.find_related_objects(
            self.db.equipments.find({'equipmentCategory': equipmentCategory}), self.EQUIPMENT_ARRAY)
        relatedChannels = ModelBackend.find_related_objects_based_on_subcategory(exerciseSubcategory, self.db.channels,
                                                                                 ['exerciseCategory', exerciseCategory],
                                                                                 ['exerciseSubcategory',
                                                                                  exerciseSubcategory],
                                                                                 self.CHANNEL_ARRAY)
        return [relatedExercises, relatedEquipments, relatedChannels]

    def __get_related_objects_for_channel_instance(self, id):
        db = self.db
        attributes = ModelBackend.get_current_instance_object_attributes(id, db.channels,
                                                                         ('exerciseCategory', 'exerciseSubcategory'))
        category = attributes[0]
        subcategory = attributes[1]

        relatedExercises = ModelBackend.find_related_objects_based_on_subcategory(subcategory, db.exercises,
                                                                                  ['category', category],
                                                                                  ['subcategory', subcategory],
                                                                                  self.EXERCISES_ARRAY)

        # Use the first related exercise object to determine what equipmentCategory to use when querying equipments collection
        topExerciseDoc = db.exercises.find_one({'_id': relatedExercises[0].id})
        if topExerciseDoc:
            equipmentCategory = topExerciseDoc['equipment'][
                0]  # Select the first equipment term in the equipment array attribute to use

        relatedEquipments = ModelBackend.find_related_objects(
            db.equipments.find({'equipmentCategory': equipmentCategory}), self.EQUIPMENT_ARRAY)
        relatedChannels = ModelBackend.find_related_objects_based_on_subcategory(subcategory, db.channels,
                                                                                 ['exerciseCategory', category],
                                                                                 ['exerciseSubcategory', subcategory],
                                                                                 self.CHANNEL_ARRAY)

        return [relatedExercises, relatedEquipments, relatedChannels]

    def __handle_filter_operation(self, modelType, flaskRequest, currentArray, pageNumber):
        # At this point modelType has already been checked to be one of these cases
        filteredArray = []
        if modelType == 'exercise':
            filteredArray = self.__get_filtered_exercises(flaskRequest.form, currentArray)
        elif modelType == 'equipment':
            filteredArray = self.__get_filtered_equipments(flaskRequest.form, currentArray)
        elif modelType == 'channel':
            filteredArray = self.__get_filtered_channels(flaskRequest.form, currentArray)
        return ModelBackend.render_model_page(pageNumber, filteredArray, 0, modelType)

    def __handle_sort_operation(self, modelType, flaskRequest, currentArray, pageNumber):
        selectedSortingAttribute = flaskRequest.form.get(self.sortCriteriaMenuKeyTemplate.format(modelType))
        if selectedSortingAttribute is None:
            return ModelBackend.render_model_page(pageNumber, currentArray, 0, modelType)
        elif flaskRequest.form.get(self.sortingHiddenFieldKeyTemplate.format(modelType)) == 'ascending':
            sortedArray = sorted(currentArray, key=lambda modelObj: getattr(modelObj, selectedSortingAttribute),
                                 reverse=False)
            return ModelBackend.render_model_page(pageNumber, sortedArray, 0, modelType)
        elif flaskRequest.form.get(self.sortingHiddenFieldKeyTemplate.format(modelType)) == 'descending':
            sortedArray = sorted(currentArray, key=lambda modelObj: getattr(modelObj, selectedSortingAttribute),
                                 reverse=True)
            return ModelBackend.render_model_page(pageNumber, sortedArray, 0, modelType)
        else:  # selected sorting attribute was not None, or the sorting button clicked did not send ascending or descending
            raise NameError('Unsupported selected sorting attribute submitted in POST request!')

    def __handle_search_operation(self, modelType, flaskRequest, currentArray, pageNumber):
        searchTerms = flaskRequest.form.get(self.searchItemsKeyTemplate.format(modelType))
        searchedArray = []
        arr = searchTerms.split('|')
        for item in arr:
            for obj in currentArray:
                if obj.name == item:
                    searchedArray.append(obj)
                    break
        return ModelBackend.render_model_page(pageNumber, searchedArray, 0, modelType)
