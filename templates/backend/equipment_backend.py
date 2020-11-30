from flask import render_template
from templates.backend.model_backend import ModelBackend
from templates.models.equipment import Equipment
import numpy as np


class EquipmentBackend(ModelBackend, Equipment):
    # filterIsActive = False
    # searchIsActive = False
    # sortIsActive = False
    # sortingAttribute = ""
    # sortingDirection = ""

    searchItemsKey = 'equipmentsSearchItems'
    sortingHiddenFieldKey = 'equipmentsSortingHiddenField'
    sortCriteriaMenuKey = 'equipmentsSortCriteriaMenu'

    # modifiedArray = []

    @staticmethod
    def load_and_return_model_array_from_db(db):
        """
        Return a python list of all Equipment objects.
        :param db: The database to load all equipments from
        :return: A python list of Equipment objects
        """
        equipment_array = []
        equipmentsCursor = db.equipments.find()
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
        # Refactor this later, but try to ensure ModelBackend global arrays are intialized for now
        ModelBackend.EQUIPMENT_ARRAY = equipment_array
        return equipment_array

    @staticmethod
    def reset_all_flags():
        EquipmentBackend.filterIsActive = False
        EquipmentBackend.sortIsActive = False
        EquipmentBackend.searchIsActive = False

    @staticmethod
    def initialize_array_from_mongo_database(db):
        """
        Return a python list of all Equipment objects.
        :param db: The database to load all equipments from
        :return: A python list of Equipment objects
        """
        equipment_array = []
        equipmentsCursor = db.equipments.find()
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
        
        ModelBackend.EQUIPMENT_ARRAY = equipment_array

    @staticmethod    
    def get_related_objects_for_instance(id, db):
        attributes = ModelBackend.find_current_instance_object(id, db.equipments, ['equipmentCategory'])
        equipmentCategory = attributes[0]

        relatedExercises = ModelBackend.find_related_objects(db.exercises.find({'equipment': equipmentCategory}), ModelBackend.EXERCISES_ARRAY)

        # Use the first related exercise object to determine what exercise category/subcategory to use when querying channels collection
        topExerciseDoc = db.exercises.find_one({'_id': relatedExercises[0].id})
        if topExerciseDoc:
            exerciseCategory = topExerciseDoc['category']
            exerciseSubcategory = topExerciseDoc['subcategory']

        relatedEquipments = ModelBackend.find_related_objects(db.equipments.find({'equipmentCategory': equipmentCategory}), ModelBackend.EQUIPMENT_ARRAY, ModelBackend.EQUIPMENT_ARRAY)
        relatedChannels = ModelBackend.find_related_objects_based_on_subcategory(exerciseSubcategory, db.channels, ['exerciseCategory', exerciseCategory], ['exerciseSubcategory', exerciseSubcategory], ModelBackend.CHANNEL_ARRAY)

        return [relatedExercises, relatedEquipments, relatedChannels]

    @staticmethod
    def filter(db, filterRequestForm, currentArray):
        # Setting up for filtering
        selectedPriceRanges = filterRequestForm.getlist("checkedPriceRange")
        selectedEquipmentCategories = filterRequestForm.getlist("checkedEquipmentCategories")

        # Query the entire exercises collection on each of the selected exercise category terms and append matching objects with matching price ranges
        filteredEquipments = []
        for priceString in selectedPriceRanges:
            priceRangeList = priceString.split(" ")
            filteredEquipments += ModelBackend.find_related_objects(db.equipments.find({'price': {'$gte': float(priceRangeList[0]), '$lt': float(priceRangeList[1])}}), currentArray, ModelBackend.EQUIPMENT_ARRAY)

        # Query the entire exercises collection on each of the selected equipment category terms and add the Exercise objects with matching equipment categories
        # NOTE THAT WE ARE TAKING THE UNION OF SELECTED FILTERING CHECKBOXES NOT THE INTERSECTION
        for equipmentCategory in selectedEquipmentCategories:
            filteredEquipments += ModelBackend.find_related_objects(db.equipments.find({'equipmentCategory': equipmentCategory}), currentArray, ModelBackend.EQUIPMENT_ARRAY)

        # Return all of filtered Exercise objects
        return list(set(filteredEquipments))

    @staticmethod
    def render_model_page(pageNumber, currentArray, resetLocalStorageFlag):
        start, end, numPages = ModelBackend.paginate(pageNumber, currentArray)
        return render_template('equipments.html',
                               currentEquipmentArray=currentArray,
                               start=start,
                               end=end,
                               pageNumber=pageNumber,
                               numPages=numPages,
                               resetLocalStorageFlag=resetLocalStorageFlag)

    @staticmethod
    def render_instance_page(instance_obj, related_objects):
        return render_template('equipmentInstance.html', equipmentObject=instance_obj, relatedObjects=related_objects)
