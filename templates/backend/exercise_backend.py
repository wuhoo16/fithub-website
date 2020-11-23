from flask import render_template
import numpy as np
from .model_interface import ModelInterface
from ..exercise import Exercise

class ExerciseBackend(ModelInterface, Exercise):
    filterIsActive = False
    searchIsActive = False
    sortIsActive = False
    sortingAttribute = ""
    sortingDirection = ""

    searchItemsKey = 'exercisesSearchItems'
    sortingHiddenFieldKey = 'exercisesSortingHiddenField'
    sortCriteriaMenuKey = 'exercisesSortCriteriaMenu'

    modifiedArray = []


    @staticmethod
    def load_from_db(db):
        """
        Return a python list of all Exercise objects.
        :param db: The database to load all exercises from
        :return: A python list of Exercise objects
        """
        exercise_array = []
        exercisesCursor = db.exercises.find()
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
        
        ModelInterface.EXERCISES_ARRAY = exercise_array


    @staticmethod
    def get_related_objects_for_instance(id, db):
        attributes = ModelInterface.find_current_instance_object(id, db.exercises, ('category', 'subcategory', 'equipment'))
        category = attributes[0]
        subcategory = attributes[1]
        equipmentCategoryList = attributes[2]

        relatedExercises = ModelInterface.find_related_objects_based_on_subcategory(subcategory, db.exercises, ['category', category], ['subcategory', subcategory], ModelInterface.EXERCISES_ARRAY)
        
        relatedEquipments = []
        for equipmentCategory in equipmentCategoryList:
            relatedEquipments = np.append(np.array(relatedEquipments), np.array(ModelInterface.find_related_objects(db.equipments.find({'equipmentCategory': equipmentCategory}), ModelInterface.EQUIPMENT_ARRAY)))

        relatedChannels = ModelInterface.find_related_objects_based_on_subcategory(subcategory, db.channels, ['exerciseCategory', category], ['exerciseSubcategory', subcategory], ModelInterface.CHANNEL_ARRAY)

        return [relatedExercises, relatedEquipments, relatedChannels]


    @staticmethod
    def filter(db, requestForm):
        #setting up to filter
        selectedExerciseCategories = requestForm.getlist("selectedExerciseCategories")
        selectedEquipmentCategories = requestForm.getlist("selectedEquipmentCategories")

        if len(selectedExerciseCategories) == 0 and len(selectedEquipmentCategories) == 0:
            searchIsActive = True

        tempModifiedArray = []
        if searchIsActive:
            tempModifiedArray = modifiedArray
        
        #beginning to filter
        filteredExercises = []

        # Query the entire exercises collection on each of the selected exercise category terms and append matching Exercise objects
        for exerciseCategory in selectedExerciseCategories:
            filteredExercises = np.array(ModelInterface.find_related_objects(db.exercises.find({'category': exerciseCategory}), ModelInterface.EXERCISES_ARRAY))

        # Query the entire exercises collection on each of the selected equipment category terms and append matching Exercise objects
        for equipmentCategory in selectedEquipmentCategories:
            filteredExercises = np.append(filteredExercises, np.array(ModelInterface.find_related_objects(db.exercises.find({'equipment': equipmentCategory}), ModelInterface.EXERCISES_ARRAY)))

        # Return all of filtered Exercise objects
        return tempModifiedArray, filteredExercises

    @staticmethod
    def render_model_page(page_number, ARR):
        start, end, num_pages = ModelInterface.paginate(page_number, ARR)
        return render_template('exercises.html', exercisesArray=ARR, start=start, end=end, page_number=page_number, num_pages=num_pages)


    @staticmethod
    def render_instance_page(instanceObj, relatedObjects):
        return render_template('exerciseInstance.html', e=instanceObj, relatedObjects=relatedObjects)
