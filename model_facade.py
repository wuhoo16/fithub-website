from templates.api.exercise_api import ExerciseAPI
from templates.api.equipment_api import EquipmentAPI 
from templates.api.channel_api import ChannelAPI 
from templates.backend import exercise_backend 
from templates.backend import equipment_backend
from templates.backend import channel_backend

from flask import render_template

class ModelFacade():
    # All methods to setup mongoDB remote database is done below.
    # Note that 'setup_database()' should only be run ONCE (unless you want to reinitialize remote database)
    # ======================================================================================================
    
    @staticmethod
    def initialize_clusters(db, *args):
        """
        Setup the remote mongoDB by initializing all the model collections passed into args argument.
        :param db: The mongo database to add the collection to
        :param args: An array of strings which specifies which models you want to initialize the clusters for
        :return: None
        """
        for api_model in args[0]:
            if api_model == "exercise":
                ExerciseAPI.initialize_mongoDB_collection(db)
            elif api_model == "equipment":
                EquipmentAPI.initialize_mongoDB_collection(db)
            elif api_model == "channel":
                ChannelAPI.initialize_mongoDB_collection(db)
            else:
                raise NameError("ERROR: " + api_model + " is not a model!")

    
    @staticmethod
    def clean_database(db):
        """
        Cleans the current phase's database by dropping all 3 model collections
        :param db: The mongo database to add the collection to
        :return: None
        """
        db.exercises.drop()
        db.equipments.drop()
        db.channels.drop()

    
    # All methods done on backend to work with model arrays is done below
    # ======================================================================================================    

    @staticmethod
    def render_homepage(db):
        ModelFacade.__initialize_model_arrays_if_required(db)
        return render_template('homepage.html', exerciseArray=exercise_backend.ModelBackend.EXERCISES_ARRAY, 
            equipmentArray=equipment_backend.ModelBackend.EQUIPMENT_ARRAY, channelArray=channel_backend.ModelBackend.CHANNEL_ARRAY)


    @staticmethod
    def render_about_page():
        return render_template('about.html')


    @staticmethod
    def render_model_page(model, page_number, request_param, db, curr_arr, operation_used):
        ModelFacade.__initialize_model_arrays_if_required(db)
        if model == "exercise":
            return ModelFacade.__model_page(request_param, exercise_backend.ExerciseBackend, curr_arr, page_number, db, operation_used)
        elif model == "equipment":
            return ModelFacade.__model_page(request_param, equipment_backend.EquipmentBackend, curr_arr, page_number, db, operation_used)
        elif model == "channel":
            return ModelFacade.__model_page(request_param, channel_backend.ChannelBackend, curr_arr, page_number, db, operation_used)
        else:
            raise NameError("ERROR: " + model + " is not a model!")

    
    @staticmethod
    def render_model_instance_page(model, array_index, db):
        if model == "exercise":
            return ModelFacade.__instance_page(exercise_backend.ModelBackend.EXERCISES_ARRAY[array_index], exercise_backend.ExerciseBackend, db)
        elif model == "equipment":
            return ModelFacade.__instance_page(equipment_backend.ModelBackend.EQUIPMENT_ARRAY[array_index], equipment_backend.EquipmentBackend, db)
        elif model == "channel":
            return ModelFacade.__instance_page(channel_backend.ModelBackend.CHANNEL_ARRAY[array_index], channel_backend.ChannelBackend, db)
        else:
            raise NameError("ERROR: " + model + " is not a model!")


    # Private helper methods
    # ======================================================================================================

    @staticmethod
    def __initialize_model_arrays_if_required(db):
        print(exercise_backend.ModelBackend.EXERCISES_ARRAY)
        print(equipment_backend.ModelBackend.EQUIPMENT_ARRAY)
        print(channel_backend.ModelBackend.CHANNEL_ARRAY)
        if len(exercise_backend.ModelBackend.EXERCISES_ARRAY) == 0:
            exercise_backend.ExerciseBackend.load_from_db(db)
            print(exercise_backend.ExerciseBackend.EXERCISES_ARRAY)
            exercise_backend.filterIsActive = False
            exercise_backend.searchIsActive = False
            exercise_backend.sortIsActive = False
        if len(equipment_backend.ModelBackend.EQUIPMENT_ARRAY) == 0:
            EQUIPMENT_ARRAY = equipment_backend.EquipmentBackend.load_from_db(db)
            equipment_backend.filterIsActive = False
            equipment_backend.searchIsActive = False
            equipment_backend.sortIsActive = False
        if len(channel_backend.ModelBackend.CHANNEL_ARRAY) == 0:
            CHANNEL_ARRAY = channel_backend.ChannelBackend.load_from_db(db)
            channel_backend.filterIsActive = False
            channel_backend.searchIsActive = False
            channel_backend.sortIsActive = False


    @staticmethod
    def __model_page(request_param, model, curr_arr, page_number, db, operation_used):
        if request_param.method == 'POST':
            if operation_used == "search":
                new_arr = ModelFacade.__get_search(request_param.form.get(model.searchItemsKey), curr_arr)
                return model.render_model_page(page_number, new_arr)
            # elif operation_used == "sort":

            # elif operation_used == "filter":

            else:
                raise NameError("operation_used param is not valid")

        elif request_param.method == 'GET':
            if operation_used == "pagination":
                print("pagination")
                # will render model page w/ resetStorageFlag = 0
            else:
                # will render model page w/ resetStorageFlag = 1
                return model.render_model_page(page_number, curr_arr)

        #     else:
        #         raise NameError("operation_used param is not valid")

        #     if request_param.form.get(model.searchItemsKey):
        #         #searching
        #         print("IN SEARCHING")
        #         # model.searchIsActive = True
        #         NEW_ARR = ModelFacade.__get_search(request_param.form.get(model.searchItemsKey), curr_arr)
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
        #             modifiedArray = ModelFacade.__search_filter_match(modifiedArray, tempModifiedArray)

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
        

    @staticmethod
    def __instance_page(instance_obj, model, db):
        """
        Find current channel instance object and call method to retrieve 2D List of related indices
        """
        relatedObjects = model.get_related_objects_for_instance(instance_obj.id, db)
        return model.render_instance_page(instance_obj, relatedObjects)


    # Helper methods for paginating all 3 model pages

    @staticmethod
    def __get_search(temp_arr, main_arr):
        totalArray = []
        arr = temp_arr.split('|')

        for item in arr:
            for obj in main_arr:
                if obj.name == item:
                    totalArray.append(obj)
                    break
        return totalArray


    @staticmethod
    def __search_filter_match(filter_arr, search_arr):
        totalArr = []

        for filtObj in filter_arr:
            for searchObj in search_arr:
                if filtObj == searchObj:
                    totalArr.append(filtObj)
                    break
        
        return totalArr
