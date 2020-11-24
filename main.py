from flask import Flask, render_template, request
from pymongo import MongoClient
from templates.backend import exercise_backend
from templates.backend.exercise_backend import ModelInterface
from templates.backend.equipment_backend import EquipmentBackend
from templates.backend.exercise_backend import ExerciseBackend
from templates.backend.channel_backend import ChannelBackend
from templates.backend import equipment_backend
from templates.backend import channel_backend

EXERCISE_INSTANCE_URL_TEMPLATE = '/exerciseinstance/{}'
EQUIPMENT_INSTANCE_URL_TEMPLATE = '/equipmentinstance/{}'
CHANNEL_INSTANCE_URL_TEMPLATE = '/channelinstance/{}'

client = MongoClient("mongodb+srv://Admin:Pass1234@apidata.lr4ia.mongodb.net/phase2Database?retryWrites=true&w=majority")
DATABASE = client.phase2Database

# Flask and view methods for home, models, model instances, and about pages below
# ====================================================================================================================
app = Flask("__name__")


# homepage
@app.route("/", methods=['GET'])
def index():
    if len(ModelInterface.EXERCISES_ARRAY) == 0:
        ExerciseBackend.initialize_array_from_mongo_database(DATABASE)
        ExerciseBackend.reset_all_flags()  # resets the filter, sort, and search flags to False for ExerciseBackend
    if len(ModelInterface.EQUIPMENT_ARRAY) == 0:
        EquipmentBackend.initialize_array_from_mongo_database(DATABASE)
        EquipmentBackend.reset_all_flags()  # resets the filter, sort, and search flags to False for EquipmentBackend
    if len(ModelInterface.CHANNEL_ARRAY) == 0:
        ChannelBackend.initialize_array_from_mongo_database(DATABASE)
        ChannelBackend.reset_all_flags()  # resets the filter, sort, and search flags to False for ChannelBackend
    return render_template('homepage.html', exerciseFilterIsActive=str.lower(str(ExerciseBackend.filterIsActive)),
                           equipmentFilterIsActive=str.lower(str(EquipmentBackend.filterIsActive)),
                           channelFilterIsActive=str.lower(str(ChannelBackend.filterIsActive)),
                           exerciseSearchIsActive=str.lower(str(ExerciseBackend.searchIsActive)),
                           equipmentSearchIsActive=str.lower(str(EquipmentBackend.searchIsActive)),
                           channelSearchIsActive=str.lower(str(ChannelBackend.searchIsActive)),
                           exerciseSortIsActive=str.lower(str(ExerciseBackend.sortIsActive)),
                           equipmentSortIsActive=str.lower(str(EquipmentBackend.sortIsActive)),
                           channelSortIsActive=str.lower(str(ChannelBackend.sortIsActive)))


# exercises model page
@app.route("/exercises/<int:page_number>", methods=['GET', 'POST'])
def exercises(page_number):
    return model_page(request, ExerciseBackend, ModelInterface.EXERCISES_ARRAY, page_number)


# equipments model page
@app.route("/equipment/<int:page_number>", methods=['GET', 'POST'])
def equipments(page_number):
    return model_page(request, EquipmentBackend, ModelInterface.EQUIPMENT_ARRAY, page_number)


# channels model page
@app.route("/channels/<int:page_number>", methods=['GET', 'POST'])
def channels(page_number):
    return model_page(request, ChannelBackend, ModelInterface.CHANNEL_ARRAY, page_number)


def model_page(flaskRequest, backendClassName, MODEL_ARR, pageNumber):
    if flaskRequest.method == 'POST':
        if flaskRequest.form.get(backendClassName.searchItemsKey):
            backendClassName.searchIsActive = True
            NEW_ARR = getSearch(flaskRequest.form.get(backendClassName.searchItemsKey), MODEL_ARR)
            backendClassName.modifiedArray = NEW_ARR
            return backendClassName.render_model_page(pageNumber, NEW_ARR)
            
        elif flaskRequest.form.get(backendClassName.sortingHiddenFieldKey):  # If this field in the posted form is set, then the user has clicked one of the sorting buttons
            backendClassName.sortingAttribute = flaskRequest.form.get(backendClassName.sortCriteriaMenuKey)

            if backendClassName.filterIsActive or backendClassName.searchIsActive:
                sortThisArray = backendClassName.modifiedArray
            else:
                sortThisArray = MODEL_ARR
            if backendClassName.sortingAttribute is None:
                backendClassName.modifiedArray = sortThisArray
            else: 
                if flaskRequest.form.get(backendClassName.sortingHiddenFieldKey) == 'ascending':
                    backendClassName.sortingDirection = 'ascending'
                    backendClassName.modifiedArray = sorted(sortThisArray,
                                                            key=lambda modelObj: getattr(modelObj, backendClassName.sortingAttribute),
                                                            reverse=False)
                elif flaskRequest.form.get(backendClassName.sortingHiddenFieldKey) == 'descending':
                    backendClassName.sortingDirection = 'descending'
                    backendClassName.modifiedArray = sorted(sortThisArray,
                                                            key=lambda modelObj: getattr(modelObj, backendClassName.sortingAttribute),
                                                            reverse=True)
                backendClassName.sortIsActive = True

            return backendClassName.render_model_page(pageNumber, backendClassName.modifiedArray)
        
        elif flaskRequest.form.get('resetHiddenField') == 'resetClicked':  # If this field is set, then the user has clicked the Reset button
            backendClassName.reset_all_flags()
            return backendClassName.render_model_page(pageNumber, MODEL_ARR)
            
        else:  # filter form was submitted using the Filter button
            backendClassName.filterIsActive = True

            # Call the helper function in the backend to query mongodb and get Array of filtered exercise objects
            tempModifiedArray, modifiedArray = backendClassName.filter(DATABASE, flaskRequest.form)

            if backendClassName.searchIsActive:
                modifiedArray = searchFilterMatch(modifiedArray, tempModifiedArray)

            # If we sorted before, sort by the same sort method again
            if backendClassName.sortIsActive:
                if backendClassName.sortingDirection == 'ascending':
                    modifiedArray = sorted(modifiedArray,
                                           key=lambda modelObj: getattr(modelObj, backendClassName.sortingAttribute),
                                           reverse=False)
                elif backendClassName.sortingDirection == 'descending':
                    modifiedArray = sorted(modifiedArray,
                                           key=lambda modelObj: getattr(modelObj, backendClassName.sortingAttribute),
                                           reverse=True)

            backendClassName.modifiedArray = modifiedArray
            return backendClassName.render_model_page(pageNumber, modifiedArray)
    
    elif flaskRequest.method == 'GET':
        if backendClassName.filterIsActive or backendClassName.sortIsActive or backendClassName.searchIsActive:
            return backendClassName.render_model_page(pageNumber, backendClassName.modifiedArray)
        else:  # else, render template using the original global array with every Exercise object
            return backendClassName.render_model_page(pageNumber, MODEL_ARR)


# about page
@app.route("/about", methods=['GET'])
def about():
    return render_template('about.html')


def getSearch(tempArr, mainArr):
    totalArray = []
    arr = tempArr.split('|')
    searchedInstanceNamesSet = set(arr)

    for obj in mainArr:
        if obj.name in searchedInstanceNamesSet:
            totalArray.append(obj)
    return totalArray


def searchFilterMatch(filterArr, searchArr):
    totalArr = []
    searchSet = set(searchArr)

    for filtObj in filterArr:
        if filtObj in searchSet:
            totalArr.append(filtObj)

    return totalArr


# All view methods for INSTANCE pages are defined below:
# ==================================================================================================================
# exercise instance pages
@app.route(EXERCISE_INSTANCE_URL_TEMPLATE.format('<int:arrayIndex>'), methods=['GET'])
def exercise_instance(arrayIndex):
    return instance_page(ModelInterface.EXERCISES_ARRAY[arrayIndex], ExerciseBackend)


# equipment instance pages
@app.route(EQUIPMENT_INSTANCE_URL_TEMPLATE.format('<int:arrayIndex>'), methods=['GET'])
def equipment_instance(arrayIndex):
    return instance_page(ModelInterface.EQUIPMENT_ARRAY[arrayIndex], EquipmentBackend)


# channel instance pages
@app.route(CHANNEL_INSTANCE_URL_TEMPLATE.format('<int:arrayIndex>'), methods=['GET'])
def channel_instance(arrayIndex):
    return instance_page(ModelInterface.CHANNEL_ARRAY[arrayIndex], ChannelBackend)


def instance_page(instanceObj, backendClassName):
    """
    Get all related instance objects and return the rendered instance page dynamically based on the model type.
    :param instanceObj:
    :param backendClassName:
    :return:
    """
    relatedObjects = backendClassName.get_related_objects_for_instance(instanceObj.id, DATABASE)
    return backendClassName.render_instance_page(instanceObj, relatedObjects)


# Start the Flask web-application when main.py file is run
if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True, use_reloader=True)
