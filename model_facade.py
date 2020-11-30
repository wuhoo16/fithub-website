from templates.api.exercise_api import ExerciseAPI
from templates.api.equipment_api import EquipmentAPI
from templates.api.channel_api import ChannelAPI
from templates.backend.exercise_backend import ExerciseBackend
from templates.backend.equipment_backend import EquipmentBackend
from templates.backend.channel_backend import ChannelBackend
from templates.backend.model_backend import self

from flask import render_template


class ModelFacade:
    # constructor
    def __init__(self, db):
        self.EXERCISES_ARRAY = None
        self.EQUIPMENT_ARRAY = None
        self.CHANNEL_ARRAY = None
        self.db = db
        self.__initialize_model_arrays_if_required(self.db)

    def get_exercises_array(self):
        print(f'In the get function, the EXERCISES_ARRAY= { self.EXERCISES_ARRAY }')
        return self.EXERCISES_ARRAY

    def get_equipment_array(self):
        return self.EQUIPMENT_ARRAY

    def get_channel_array(self):
        return self.CHANNEL_ARRAY

    # All methods to communicate with the mongoDB remote database is defined below including:
    # 1.) setup_database(db, *args): Used to call the APIs and initialize all 3 model collections
    # 2.) clean_database(db):
    # ======================================================================================================
    # @staticmethod
    def setup_database(db, modelType=None):
        """
        Setup the remote mongoDB by initializing all the model collections passed into args argument. Note that if the 2nd parameter
        is not provided, this method will initialize all 3 collections by default.
        :param db: The mongo database to add the collection to
        :param modelType: Optional parameter to only initialize one model collection. Expects one of the following strings: 'exercises', 'equipments', 'channels'
        :return: None
        """
        if modelType is None:
            ExerciseAPI.initialize_mongoDB_collection(db)
            EquipmentAPI.initialize_mongoDB_collection(db)
            ChannelAPI.initialize_mongoDB_collection(db)
        else:
            if modelType == "exercises":
                ExerciseAPI.initialize_mongoDB_collection(db)
            elif modelType == "equipments":
                EquipmentAPI.initialize_mongoDB_collection(db)
            elif modelType == "channels":
                ChannelAPI.initialize_mongoDB_collection(db)
            else:
                raise NameError("ERROR: " + modelType + " is not a valid model type! "
                                                        "Only 'exercises', 'equipments', or 'channels' are supported parameters to pass in.")

    # @staticmethod
    def clean_database(db):
        """
        Cleans the current phase's database by dropping all 3 model collections.
        :param db: The mongo database to drop the collections from
        :return: None
        """
        db.exercises.drop()
        db.equipments.drop()
        db.channels.drop()

    # All Flask render methods are defined below
    # ======================================================================================================
    def render_homepage(self):
        return render_template('homepage.html')

    def render_about_page(self):
        return render_template('about.html')

    def render_model_page(self, modelType, pageNumber, flaskRequest, db, currentArray, operationUsed):
        if currentArray is None or len(currentArray):
            print(f'In render_model_page() method, the currentArray= {currentArray}')
        if modelType == "exercise":
            return self.__model_page(backendClass=ExerciseBackend,
                                            pageNumber=pageNumber,
                                            flaskRequest=flaskRequest,
                                            db=db,
                                            currentArray=currentArray,
                                            operationUsed=operationUsed,
                                            modelType=modelType)
        elif modelType == "equipment":
            return self.__model_page(backendClass=EquipmentBackend,
                                            pageNumber=pageNumber,
                                            flaskRequest=flaskRequest,
                                            db=db,
                                            currentArray=currentArray,
                                            operationUsed=operationUsed,
                                            modelType=modelType)
        elif modelType == "channel":
            print('In render_model_page() method, just entered the modelType="channel" branch...')
            return self.__model_page(backendClass=ChannelBackend,
                                            pageNumber=pageNumber,
                                            flaskRequest=flaskRequest,
                                            db=db,
                                            currentArray=currentArray,
                                            operationUsed=operationUsed,
                                            modelType=modelType)
        else:
            raise NameError("ERROR: " + modelType + " is not a supported model type!")

    def render_model_instance_page(self, modelType, array_index, db):
        if modelType == "exercise":
            return self.__instance_page(modelType=ExerciseBackend,
                                               instanceObject=self.EXERCISES_ARRAY[array_index],
                                               db=db)
        elif modelType == "equipment":
            return self.__instance_page(modelType=EquipmentBackend,
                                               instanceObject=self.EQUIPMENT_ARRAY[array_index],
                                               db=db)
        elif modelType == "channel":
            return self.__instance_page(modelType=ChannelBackend,
                                               instanceObject=self.CHANNEL_ARRAY[array_index],
                                               db=db)
        else:
            raise NameError("ERROR: " + modelType + " is not a supported model type!")

    # Private helper methods
    # ======================================================================================================
    def __initialize_model_arrays_if_required(self, db):
        self.EXERCISES_ARRAY = ExerciseBackend.load_and_return_model_array_from_db(db)
        self.EQUIPMENT_ARRAY = EquipmentBackend.load_and_return_model_array_from_db(db)
        self.CHANNEL_ARRAY = ChannelBackend.load_and_return_model_array_from_db(db)

    def __model_page(self, backendClass, pageNumber, flaskRequest, db, currentArray, operationUsed, modelType):
        print('Right at the beginning of __model_page(), the currentArray param is: { currentArray}')
        # Wrap this in a private helper function to convert array of integers to objects
        if len(currentArray) != 0:
            if isinstance(currentArray[0], int):
                currentArrayOfObjects = []
                for arrayIndex in currentArray:
                    if modelType == 'exercises':
                        currentArrayOfObjects.append(self.EXERCISES_ARRAY[arrayIndex])
                    elif modelType == 'equipment':
                        currentArrayOfObjects.append(self.EQUIPMENT_ARRAY[arrayIndex])
                    elif modelType == 'channel':
                        currentArrayOfObjects.append(self.CHANNEL_ARRAY[arrayIndex])
                currentArray = currentArrayOfObjects
            else: # Make sure currentArray is not reassigned
                pass

        # At this point currentArray should be an array of OBJECTS!!!
        if flaskRequest.method == 'POST':
            if operationUsed == "Search":
                print(f'In the operationUsed == "Search" branch, the currentArray param before __get_search() is: { currentArray }')
                print(flaskRequest.form.get(backendClass.searchItemsKey))
                arrayAfterSearch = self.__get_search(flaskRequest.form.get(backendClass.searchItemsKey), currentArray)
                print(f'In the operationUsed == "Search" branch, the arrayAfterSearch variable after __get_search() is: { arrayAfterSearch }')
                return backendClass.render_model_page(pageNumber, arrayAfterSearch)
            elif operationUsed == "Sort":
                pass
            elif operationUsed == "Filter":
                pass
            else:
                raise NameError("operationUsed param is not valid!")

        elif flaskRequest.method == 'GET':
            if operationUsed == "Pagination":
                print("In Pagination branch...")
                # will render model page w/ resetStorageFlag = 0
            else:
                # will render model page w/ resetStorageFlag = 1
                print('In the __model_page() method in the else branch for a GET request...')
                print(f'In __model_page() method, the currentArray= {currentArray}')
                return backendClass.render_model_page(pageNumber, currentArray)

        #     else:
        #         raise NameError("operation_used param is not valid")

        #     if request_param.form.get(model.searchItemsKey):
        #         #searching
        #         print("IN SEARCHING")
        #         # model.searchIsActive = True
        #         NEW_ARR = self.__get_search(request_param.form.get(model.searchItemsKey), curr_arr)
        #         # model.modifiedArray = NEW_ARR
        #         return model.render_model_page(page_number, NEW_ARR)

        #     elif request_param.form.get(model.sortingHiddenFieldKey):  # If this field in the posted form is set, then the user has clicked one of the sorting buttons
        #         print("IN SORTING")
        #         model.sortingAttribute = request_param.form.get(model.sortCriteriaMenuKey)

        #         if model.filterIsActive or model.searchIsActive:
        #             sortThisArray = model.modifiedArray
        #         else:
        #             sortThisArray = curr_arr
        #         if model.sortingAttribute is None:
        #             model.modifiedArray = sortThisArray
        #         else: 
        #             if request_param.form.get(model.sortingHiddenFieldKey) == 'ascending':
        #                 model.sortingDirection = 'ascending'
        #                 model.modifiedArray = sorted(sortThisArray,
        #                                             key=lambda modelObj: getattr(modelObj, model.sortingAttribute),
        #                                             reverse=False)
        #             elif request_param.form.get(model.sortingHiddenFieldKey) == 'descending':
        #                 model.sortingDirection = 'descending'
        #                 model.modifiedArray = sorted(sortThisArray,
        #                                             key=lambda modelObj: getattr(modelObj, model.sortingAttribute),
        #                                             reverse=True)
        #             model.sortIsActive = True

        #         return model.render_model_page(page_number, model.modifiedArray)

        #     elif request_param.form.get('resetHiddenField') == 'resetClicked':  # If this field is set, then the user has clicked the Reset button
        #         print("RESETTING")
        #         model.filterIsActive = False
        #         model.sortIsActive = False
        #         model.searchIsActive = False
        #         return model.render_model_page(page_number, curr_arr)

        #     else:  # filter form was submitted using the Filter button
        #         print("FILTERING")
        #         model.filterIsActive = True

        #         # Call the helper function in the backend to query mongodb and get Array of filtered exercise objects
        #         tempModifiedArray, modifiedArray = model.filter(db, request_param.form)

        #         if model.searchIsActive:
        #             modifiedArray = self.__search_filter_match(modifiedArray, tempModifiedArray)

        #         # If we sorted before, sort by the same sort method again
        #         if model.sortIsActive:
        #             if model.sortingDirection == 'ascending':
        #                 modifiedArray = sorted(modifiedArray,
        #                                                 key=lambda modelObj: getattr(modelObj, model.sortingAttribute),
        #                                                 reverse=False)
        #             elif model.sortingDirection == 'descending':
        #                 modifiedArray = sorted(modifiedArray,
        #                                                 key=lambda modelObj: getattr(modelObj, model.sortingAttribute),
        #                                                 reverse=True)

        #         model.modifiedArray = modifiedArray
        #         return model.render_model_page(page_number, modifiedArray)

        # elif request_param.method == 'GET':
        #     if model.filterIsActive or model.sortIsActive or model.searchIsActive:
        #         return model.render_model_page(page_number, model.modifiedArray)
        #     else:  # else, render template using the original global array with every Exercise object
        #         return model.render_model_page(page_number, curr_arr)

    def __instance_page(self, modelType, instanceObject, db):
        """
        Find current channel instance object and call method to retrieve 2D List of related indices
        """
        relatedObjects = modelType.get_related_objects_for_instance(instanceObject.id, db)
        return modelType.render_instance_page(instanceObject, relatedObjects)

    # Helper methods for paginating all 3 model pages

    def __get_search(self, delimited_search_string, main_arr):
        totalArray = []
        arr = delimited_search_string.split('|')

        for item in arr:
            for obj in main_arr:
                if obj.name == item:
                    totalArray.append(obj)
                    break
        return totalArray

    def __search_filter_match(self, filter_arr, search_arr):
        totalArr = []

        for filtObj in filter_arr:
            for searchObj in search_arr:
                if filtObj == searchObj:
                    totalArr.append(filtObj)
                    break

        return totalArr
