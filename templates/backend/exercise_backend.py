from flask import render_template
import numpy as np
from templates.backend.model_backend import ModelBackend
from templates.models.exercise import Exercise

class ExerciseBackend(ModelBackend, Exercise):
    filterIsActive = False
    sortIsActive = False
    searchIsActive = False
    sortingAttribute = ""
    sortingDirection = ""

    searchItemsKey = 'exercisesSearchItems'
    sortingHiddenFieldKey = 'exercisesSortingHiddenField'
    sortCriteriaMenuKey = 'exercisesSortCriteriaMenu'

    modifiedArray = []

    @staticmethod
    def reset_all_flags():
        ExerciseBackend.filterIsActive = False
        ExerciseBackend.sortIsActive = False
        ExerciseBackend.searchIsActive = False

    @staticmethod
    def initialize_array_from_mongo_database(db):
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
        
        ModelBackend.EXERCISES_ARRAY = exercise_array

    @staticmethod
    def get_related_objects_for_instance(id, db):
        attributes = ModelBackend.find_current_instance_object(id, db.exercises, ('category', 'subcategory', 'equipment'))
        category = attributes[0]
        subcategory = attributes[1]
        equipmentCategoryList = attributes[2]

        relatedExercises = ModelBackend.find_related_objects_based_on_subcategory(subcategory, db.exercises, ['category', category], ['subcategory', subcategory], ModelBackend.EXERCISES_ARRAY)
        
        relatedEquipments = []
        for equipmentCategory in equipmentCategoryList:
            relatedEquipments = np.append(np.array(relatedEquipments), np.array(ModelBackend.find_related_objects(db.equipments.find({'equipmentCategory': equipmentCategory}), ModelBackend.EQUIPMENT_ARRAY)))

        relatedChannels = ModelBackend.find_related_objects_based_on_subcategory(subcategory, db.channels, ['exerciseCategory', category], ['exerciseSubcategory', subcategory], ModelBackend.CHANNEL_ARRAY)

        return [relatedExercises, relatedEquipments, relatedChannels]

    @staticmethod
    def filter(db, requestForm):
        # setting up to filter
        selectedExerciseCategories = requestForm.getlist("checkedExerciseCategories")
        selectedEquipmentCategories = requestForm.getlist("checkedEquipmentCategories")

        if len(selectedExerciseCategories) == 0 and len(selectedEquipmentCategories) == 0:
            ExerciseBackend.searchIsActive = True

        tempModifiedArray = []
        if ExerciseBackend.searchIsActive:
            tempModifiedArray = ExerciseBackend.modifiedArray
        
        # beginning to filter
        filteredExercises = []

        # Query the entire exercises collection on each of the selected exercise category terms and append matching Exercise objects
        for exerciseCategory in selectedExerciseCategories:
            filteredExercises = np.array(ModelBackend.find_related_objects(db.exercises.find({'category': exerciseCategory}), ModelBackend.EXERCISES_ARRAY))

        # Query the entire exercises collection on each of the selected equipment category terms and append matching Exercise objects
        for equipmentCategory in selectedEquipmentCategories:
            filteredExercises = np.append(filteredExercises, np.array(ModelBackend.find_related_objects(db.exercises.find({'equipment': equipmentCategory}), ModelBackend.EXERCISES_ARRAY)))

        # Return all of filtered Exercise objects
        return tempModifiedArray, filteredExercises

    @staticmethod
    def render_model_page(page_number, arr):
        start, end, num_pages = ModelBackend.paginate(page_number, arr)
        return render_template('exercises.html', exercisesArray=arr, start=start, end=end, page_number=page_number, num_pages=num_pages)

    @staticmethod
    def render_instance_page(instance_obj, related_objects):
        return render_template('exerciseInstance.html', e=instance_obj, relatedObjects=related_objects)
