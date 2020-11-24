from flask import render_template
from templates.backend.model_interface import ModelInterface
from templates.equipment import Equipment
import numpy as np


class EquipmentBackend(ModelInterface, Equipment):
    filterIsActive = False
    searchIsActive = False
    sortIsActive = False
    sortingAttribute = ""
    sortingDirection = ""

    searchItemsKey = 'equipmentsSearchItems'
    sortingHiddenFieldKey = 'equipmentsSortingHiddenField'
    sortCriteriaMenuKey = 'equipmentsSortCriteriaMenu'

    modifiedArray = []

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
        
        ModelInterface.EQUIPMENT_ARRAY = equipment_array

    @staticmethod    
    def get_related_objects_for_instance(id, db):
        attributes = ModelInterface.find_current_instance_object(id, db.equipments, ['equipmentCategory'])
        equipmentCategory = attributes[0]

        relatedExercises = ModelInterface.find_related_objects(db.exercises.find({'equipment': equipmentCategory}), ModelInterface.EXERCISES_ARRAY)

        # Use the first related exercise object to determine what exercise category/subcategory to use when querying channels collection
        topExerciseDoc = db.exercises.find_one({'_id': relatedExercises[0].id})
        if topExerciseDoc:
            exerciseCategory = topExerciseDoc['category']
            exerciseSubcategory = topExerciseDoc['subcategory']

        relatedEquipments = ModelInterface.find_related_objects(db.equipments.find({'equipmentCategory': equipmentCategory}), ModelInterface.EQUIPMENT_ARRAY)
        relatedChannels = ModelInterface.find_related_objects_based_on_subcategory(exerciseSubcategory, db.channels, ['exerciseCategory', exerciseCategory], ['exerciseSubcategory', exerciseSubcategory], ModelInterface.CHANNEL_ARRAY)

        return [relatedExercises, relatedEquipments, relatedChannels]

    @staticmethod
    def filter(db, requestForm):
        print("in equipment")
        # Setting up for filtering
        selectedPriceRanges = requestForm.getlist("checkedPriceRange")
        selectedEquipmentCategories = requestForm.getlist("checkedEquipmentCategories")

        if len(selectedPriceRanges) == 0 and len(selectedEquipmentCategories) == 0:
            EquipmentBackend.searchIsActive = True

        tempModifiedArray = []
        if EquipmentBackend.searchIsActive:
            tempModifiedArray = EquipmentBackend.modifiedArray

        filteredEquipments = []

        # Query the entire exercises collection on each of the selected exercise category terms and append matching Exercise objects
        for priceString in selectedPriceRanges:
            priceRangeList = priceString.split(" ")
            filteredEquipments = np.array(ModelInterface.find_related_objects(db.equipments.find({'price': {'$gte': float(priceRangeList[0]), '$lt': float(priceRangeList[1])}}), ModelInterface.EQUIPMENT_ARRAY))

        # Query the entire exercises collection on each of the selected equipment category terms and append matching Exercise objects
        for equipmentCategory in selectedEquipmentCategories:
            filteredEquipments = np.append(filteredEquipments, np.array(ModelInterface.find_related_objects(db.equipments.find({'equipmentCategory': equipmentCategory}), ModelInterface.EQUIPMENT_ARRAY)))

        # Return all of filtered Exercise objects
        return tempModifiedArray, filteredEquipments

    @staticmethod
    def render_model_page(page_number, ARR):
        start, end, num_pages = ModelInterface.paginate(page_number, ARR)
        return render_template('equipments.html', equipmentArray=ARR, start=start, end=end, page_number=page_number, num_pages=num_pages)

    @staticmethod
    def render_instance_page(instanceObj, relatedObjects):
        return render_template('equipmentInstance.html', equipmentObject=instanceObj, relatedObjects=relatedObjects)
