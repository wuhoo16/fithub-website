from flask import Flask, render_template, request
from pymongo import MongoClient
from templates.backend import exercise_backend 
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
    if len(exercise_backend.ModelInterface.EXERCISES_ARRAY) == 0:
        exercise_backend.ExerciseBackend.load_from_db(DATABASE)
        exercise_backend.filterIsActive = False
        exercise_backend.searchIsActive = False
        exercise_backend.sortIsActive = False
    if len(equipment_backend.ModelInterface.EQUIPMENT_ARRAY) == 0:
        EQUIPMENT_ARRAY = equipment_backend.EquipmentBackend.load_from_db(DATABASE)
        equipment_backend.filterIsActive = False
        equipment_backend.searchIsActive = False
        equipment_backend.sortIsActive = False
    if len(channel_backend.ModelInterface.CHANNEL_ARRAY) == 0:
        CHANNEL_ARRAY = channel_backend.ChannelBackend.load_from_db(DATABASE)
        channel_backend.filterIsActive = False
        channel_backend.searchIsActive = False
        channel_backend.sortIsActive = False
    return render_template('homepage.html', exerciseFilterIsActive=str.lower(str(exercise_backend.filterIsActive)),
                           equipmentFilterIsActive=str.lower(str(equipment_backend.filterIsActive)),
                           channelFilterIsActive=str.lower(str(channel_backend.filterIsActive)), 
                           exerciseSearchIsActive=str.lower(str(exercise_backend.searchIsActive)),
                           equipmentSearchIsActive=str.lower(str(equipment_backend.searchIsActive)),
                           channelSearchIsActive=str.lower(str(channel_backend.searchIsActive)), 
                           exerciseSortIsActive=str.lower(str(exercise_backend.sortIsActive)),
                           equipmentSortIsActive=str.lower(str(equipment_backend.sortIsActive)),
                           channelSortIsActive=str.lower(str(channel_backend.sortIsActive)))


# exercises model page
@app.route("/exercises/<int:page_number>", methods=['GET', 'POST'])
def exercises(page_number):
    return model_page(request, exercise_backend.ExerciseBackend, exercise_backend.ModelInterface.EXERCISES_ARRAY, page_number)


# equipments model page
@app.route("/equipment/<int:page_number>", methods=['GET', 'POST'])
def equipments(page_number):
    return model_page(request, equipment_backend.EquipmentBackend, equipment_backend.ModelInterface.EQUIPMENT_ARRAY, page_number)


# channels model page
@app.route("/channels/<int:page_number>", methods=['GET', 'POST'])
def channels(page_number):
    return model_page(request, channel_backend.ChannelBackend, channel_backend.ModelInterface.CHANNEL_ARRAY, page_number)


def model_page(request, model, MODEL_ARR, page_number):
    if request.method == 'POST':
        if request.form.get(model.searchItemsKey):
            model.searchIsActive = True
            NEW_ARR = getSearch(request.form.get(model.searchItemsKey), MODEL_ARR)
            model.modifiedArray = NEW_ARR
            return model.render_model_page(page_number, NEW_ARR)
            
        elif request.form.get(model.sortingHiddenFieldKey):  # If this field in the posted form is set, then the user has clicked one of the sorting buttons
            model.sortingAttribute = request.form.get(model.sortCriteriaMenuKey)

            if model.filterIsActive or model.searchIsActive:
                sortThisArray = model.modifiedArray
            else:
                sortThisArray = MODEL_ARR
            if model.sortingAttribute is None:
                model.modifiedArray = sortThisArray
            else: 
                if request.form.get(model.sortingHiddenFieldKey) == 'ascending':
                    model.sortingDirection = 'ascending'
                    model.modifiedArray = sorted(sortThisArray,
                                                key=lambda modelObj: getattr(modelObj, model.sortingAttribute),
                                                reverse=False)
                elif request.form.get(model.sortingHiddenFieldKey) == 'descending':
                    model.sortingDirection = 'descending'
                    model.modifiedArray = sorted(sortThisArray,
                                                key=lambda modelObj: getattr(modelObj, model.sortingAttribute),
                                                reverse=True)
                model.sortIsActive = True

            return model.render_model_page(page_number, model.modifiedArray)
        
        elif request.form.get('resetHiddenField') == 'resetClicked':  # If this field is set, then the user has clicked the Reset button
            model.filterIsActive = False
            model.sortIsActive = False
            model.searchIsActive = False
            return model.render_model_page(page_number, MODEL_ARR)
            
        else:  # filter form was submitted using the Filter button
            model.filterIsActive = True

            # Call the helper function in the backend to query mongodb and get Array of filtered exercise objects
            tempModifiedArray, modifiedArray = model.filter(DATABASE, request.form)

            if model.searchIsActive:
                modifiedArray = searchFilterMatch(modifiedArray, tempModifiedArray)

            # If we sorted before, sort by the same sort method again
            if model.sortIsActive:
                if model.sortingDirection == 'ascending':
                    modifiedArray = sorted(modifiedArray,
                                                    key=lambda modelObj: getattr(modelObj, model.sortingAttribute),
                                                    reverse=False)
                elif model.sortingDirection == 'descending':
                    modifiedArray = sorted(modifiedArray,
                                                    key=lambda modelObj: getattr(modelObj, model.sortingAttribute),
                                                    reverse=True)

            model.modifiedArray = modifiedArray
            return model.render_model_page(page_number, modifiedArray)
    
    elif request.method == 'GET':
        if model.filterIsActive or model.sortIsActive or model.searchIsActive:
            return model.render_model_page(page_number, model.modifiedArray)
        else:  # else, render template using the original global array with every Exercise object
            return model.render_model_page(page_number, MODEL_ARR)


# about page
@app.route("/about", methods=['GET'])
def about():
    return render_template('about.html')


# Helper methods for paginating all 3 model pages

def getSearch(tempArr, mainArr):
    totalArray = []
    arr = tempArr.split('|')

    for item in arr:
        for obj in mainArr:
            if obj.name == item:
                totalArray.append(obj)
                break
    return totalArray

def searchFilterMatch(filterArr, searchArr):
    totalArr = []

    for filtObj in filterArr:
        for searchObj in searchArr:
            if filtObj == searchObj:
                totalArr.append(filtObj)
                break
    
    return totalArr


# All view methods for INSTANCE pages are defined below:
# ==================================================================================================================
# exercise instance pages
@app.route(EXERCISE_INSTANCE_URL_TEMPLATE.format('<int:arrayIndex>'), methods=['GET'])
def exercise_instance(arrayIndex):
    return instance_page(exercise_backend.ModelInterface.EXERCISES_ARRAY[arrayIndex], exercise_backend.ExerciseBackend)


# equipment instance pages
@app.route(EQUIPMENT_INSTANCE_URL_TEMPLATE.format('<int:arrayIndex>'), methods=['GET'])
def equipment_instance(arrayIndex):
    return instance_page(equipment_backend.ModelInterface.EQUIPMENT_ARRAY[arrayIndex], equipment_backend.EquipmentBackend)


# channel instance pages
@app.route(CHANNEL_INSTANCE_URL_TEMPLATE.format('<int:arrayIndex>'), methods=['GET'])
def channel_instance(arrayIndex):
    return instance_page(channel_backend.ModelInterface.CHANNEL_ARRAY[arraqyIndex], channel_backend.ChannelBackend)


def instance_page(instanceObj, model):
    """
    Find current channel instance object and call method to retrieve 2D List of related indices
    """
    relatedObjects = model.get_related_objects_for_instance(instanceObj.id, DATABASE)
    return model.render_instance_page(instanceObj, relatedObjects)


# Start the Flask web-application when main.py file is run
if __name__ == "__main__":

    app.run(host="localhost", port=8080, debug=True, use_reloader=True)
