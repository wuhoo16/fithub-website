from flask import Flask, request
from pymongo import MongoClient
from werkzeug.routing import BaseConverter

from model_facade import ModelFacade


# Necessary utility class to help support passing a list variable dynamically to a Flask view function. It encodes an array of Objects into a long '+%+' delimited string for view function's
# route URL to render correctly. In addition, it also converts from a long '+%+' delimited string back to either a array containing 'INITIALIZE' keyword as the first element or convert into an
# array of INTEGERS representing the arrayIndices instead of an array of STRINGS of numbers
# NOTE THAT THIS IS NECESSARY TO COMMUNICATE BETWEEN FRONTEND AND BACKEND!!! (The currentArray variable matches the last state)
class ListConverter(BaseConverter):
    def to_python(self, value):
        splitStringArray = value.split('+%+')
        if len(splitStringArray) == 0:
            print('In to_python() method, empty string passed in from frontend to backend...')
            return []
        elif splitStringArray[0] == 'INITIALIZE':
            print('In elif branch...')
            return splitStringArray
        else:  # Need to convert a string of arrayIndices to array of ints
            splitIntegerArray = []
            for string in splitStringArray:
                splitIntegerArray.append(int(string))
            return splitIntegerArray

    def to_url(self, values):
        if len(values) == 0:
            print('Warning! In to_url() method, the values parameter passed in was an empty list!')
            pass
            # Might need to handle case where the list is empty
        return '+%+'.join(super(ListConverter, self).to_url(value) for value in values)


# GLOBAL VARIABLES
EXERCISE_INSTANCE_URL_TEMPLATE = '/exerciseinstance/{}'
EQUIPMENT_INSTANCE_URL_TEMPLATE = '/equipmentinstance/{}'
CHANNEL_INSTANCE_URL_TEMPLATE = '/channelinstance/{}'
client = MongoClient(
    "mongodb+srv://Admin:Pass1234@apidata.lr4ia.mongodb.net/phase2Database?retryWrites=true&w=majority")
DATABASE = client.phase2Database
EXERCISES_ARRAY = None
EQUIPMENT_ARRAY = None
CHANNEL_ARRAY = None
MODEL_FACADE_INSTANCE = None


# Helper function to setup global variables once per server session. Note that this should be called at the beginning of
# EVERY view function. The function will check if every global var is still None before initializing
def setup():
    # Ensure main.py has an accessible global arrays for all 3 model types
    global EXERCISES_ARRAY, EQUIPMENT_ARRAY, CHANNEL_ARRAY, MODEL_FACADE_INSTANCE
    if MODEL_FACADE_INSTANCE is None and EXERCISES_ARRAY is None and EQUIPMENT_ARRAY is None and CHANNEL_ARRAY is None:
        MODEL_FACADE_INSTANCE = ModelFacade(DATABASE)  # This ModelFacade instance initializes 3 model arrays from the mongoDB
        EXERCISES_ARRAY = MODEL_FACADE_INSTANCE.get_exercises_array()
        EQUIPMENT_ARRAY = MODEL_FACADE_INSTANCE.get_equipment_array()
        CHANNEL_ARRAY = MODEL_FACADE_INSTANCE.get_channel_array()
    else:
        print('THE GLOBAL ARRAYS AND MODEL_FACADE_INSTANCE VARIABLES ARE ALREADY INITIALIZED! Skipping setup() method...')


# Set the Flask application and enable 'list' as a supported routing rule/URL variable type
# ==========================================================================================================
app = Flask("__name__")
app.url_map.converters['list'] = ListConverter


# Flask and view methods for home, models, model instances, and about pages below
# ====================================================================================================================
# homepage
@app.route("/", methods=['GET'])
def index():
    setup()
    return ModelFacade.render_homepage()


# about page
@app.route("/about", methods=['GET'])
def about():
    setup()
    return ModelFacade.render_about_page()


# exercises model page
@app.route("/exercises/<int:pageNumber>/<list:currentArray>/<string:operationUsed>", methods=['GET', 'POST'])
def exercises(pageNumber, currentArray, operationUsed):
    setup()
    global EXERCISES_ARRAY
    if currentArray[0] == 'INITIALIZE':
        currentArray = EXERCISES_ARRAY

    return MODEL_FACADE_INSTANCE.render_model_page(modelType="exercise",
                                                   pageNumber=pageNumber,
                                                   flaskRequest=request,
                                                   currentArray=currentArray,
                                                   operationUsed=operationUsed)


# equipments model page
@app.route("/equipment/<int:pageNumber>/<list:currentArray>/<string:operationUsed>", methods=['GET', 'POST'])
def equipments(pageNumber, currentArray, operationUsed):
    setup()
    global EQUIPMENT_ARRAY
    if currentArray[0] == 'INITIALIZE':
        currentArray = EQUIPMENT_ARRAY
    return MODEL_FACADE_INSTANCE.render_model_page(modelType="equipment",
                                                   pageNumber=pageNumber,
                                                   flaskRequest=request,
                                                   currentArray=currentArray,
                                                   operationUsed=operationUsed)


# channels model page
@app.route("/channels/<int:pageNumber>/<list:currentArray>/<string:operationUsed>", methods=['GET', 'POST'])
def channels(pageNumber, currentArray, operationUsed):
    setup()
    global CHANNEL_ARRAY
    if currentArray[0] == 'INITIALIZE':
        currentArray = CHANNEL_ARRAY
    return MODEL_FACADE_INSTANCE.render_model_page(modelType="channel",
                                                   pageNumber=pageNumber,
                                                   flaskRequest=request,
                                                   currentArray=currentArray,
                                                   operationUsed=operationUsed)


# All view methods for INSTANCE pages are defined below:
# ==================================================================================================================
# exercise instance pages
@app.route(EXERCISE_INSTANCE_URL_TEMPLATE.format('<int:arrayIndex>'), methods=['GET'])
def exercise_instance(arrayIndex):
    return MODEL_FACADE_INSTANCE.render_instance_page("exercise", arrayIndex)


# equipment instance pages
@app.route(EQUIPMENT_INSTANCE_URL_TEMPLATE.format('<int:arrayIndex>'), methods=['GET'])
def equipment_instance(arrayIndex):
    return MODEL_FACADE_INSTANCE.render_instance_page("equipment", arrayIndex)


# channel instance pages
@app.route(CHANNEL_INSTANCE_URL_TEMPLATE.format('<int:arrayIndex>'), methods=['GET'])
def channel_instance(arrayIndex):
    return MODEL_FACADE_INSTANCE.render_instance_page("channel", arrayIndex)


# Start the Flask web-application when main.py file is run
if __name__ == "__main__":
    # SEE mongodb_initialization_driver.py for all code to initializize the mongoDB collections

    # Start the Flask app server
    app.run(host="localhost", port=8080, debug=True, use_reloader=True)
