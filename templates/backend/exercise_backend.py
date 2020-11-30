from flask import render_template
from templates.backend.model_backend import ModelBackend
from templates.models.exercise import Exercise


class ExerciseBackend(ModelBackend, Exercise):
    searchItemsKey = 'exercisesSearchItems'
    sortingHiddenFieldKey = 'exercisesSortingHiddenField'
    sortCriteriaMenuKey = 'exercisesSortCriteriaMenu'

    @staticmethod
    def load_and_return_model_array_from_db(db):
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
        # TODO: Refactor this later, but try to ensure ModelBackend global arrays are initialized for now
        ModelBackend.EXERCISES_ARRAY = exercise_array
        return exercise_array

    @staticmethod
    def get_related_objects_for_instance(id, db):
        attributes = ModelBackend.get_current_instance_object_attributes(id, db.exercises, ('category', 'subcategory', 'equipment'))
        category = attributes[0]
        subcategory = attributes[1]
        equipmentCategoryList = attributes[2]

        relatedExercises = ModelBackend.find_related_objects_based_on_subcategory(subcategory, db.exercises, ['category', category], ['subcategory', subcategory], ModelBackend.EXERCISES_ARRAY)
        
        relatedEquipments = []
        for equipmentCategory in equipmentCategoryList:
            relatedEquipments += ModelBackend.find_related_objects(db.equipments.find({'equipmentCategory': equipmentCategory}), ModelBackend.EQUIPMENT_ARRAY, ModelBackend.EXERCISES_ARRAY)

        relatedChannels = ModelBackend.find_related_objects_based_on_subcategory(subcategory, db.channels, ['exerciseCategory', category], ['exerciseSubcategory', subcategory], ModelBackend.CHANNEL_ARRAY)

        return [relatedExercises, relatedEquipments, relatedChannels]

    @staticmethod
    def filter(db, filterRequestForm, currentArray):
        # setting up to filter
        selectedExerciseCategories = filterRequestForm.getlist("checkedExerciseCategories")
        selectedEquipmentCategories = filterRequestForm.getlist("checkedEquipmentCategories")

        # Query the entire exercises collection on each of the selected exercise category terms and append matching Exercise objects
        filteredExercises = []
        for exerciseCategory in selectedExerciseCategories:
            filteredExercises += ModelBackend.find_related_objects(db.exercises.find({'category': exerciseCategory}), currentArray, ModelBackend.EXERCISES_ARRAY)

        # Query the entire exercises collection on each of the selected equipment category terms and append matching Exercise objects
        # NOTE THAT WE ARE TAKING THE UNION OF SELECTED FILTERING CHECKBOXES NOT THE INTERSECTION
        for equipmentCategory in selectedEquipmentCategories:
            filteredExercises += ModelBackend.find_related_objects(db.exercises.find({'equipment': equipmentCategory}), currentArray, ModelBackend.EXERCISES_ARRAY)

        # Return all of matching Exercise objects after filtering on the currentArray
        return list(set(filteredExercises))

    @staticmethod
    def render_model_page(pageNumber, currentArray, resetLocalStorageFlag):
        start, end, numPages = ModelBackend.paginate(pageNumber, currentArray)
        return render_template('exercises.html',
                               currentExercisesArray=currentArray,
                               start=start,
                               end=end,
                               pageNumber=pageNumber,
                               numPages=numPages,
                               resetLocalStorageFlag=resetLocalStorageFlag)

    # TODO: NEED TO ADD A 'modelType' string parameter to form the html file name DYNAMICALLY BEFORE PULLING IT OUT
    @staticmethod
    def render_instance_page(instanceObject, relatedObjects):
        return render_template('exerciseInstance.html', instanceObject=instanceObject, relatedObjects=relatedObjects)
