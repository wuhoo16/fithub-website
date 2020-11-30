from flask import Flask, request
from pymongo import MongoClient
from werkzeug.routing import BaseConverter

from model_facade import ModelFacade


class ListConverter(BaseConverter):
    def to_python(self, value):
        splitStringArray = value.split('+%+')
        if len(splitStringArray) == 0:
            print('While converting the list parameter from frontend to backed with the ListConverter, empty array given.')
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
            pass
            # Might need to handle case where the list is empty
        return '+%+'.join(super(ListConverter, self).to_url(value) for value in values)


EXERCISE_INSTANCE_URL_TEMPLATE = '/exerciseinstance/{}'
EQUIPMENT_INSTANCE_URL_TEMPLATE = '/equipmentinstance/{}'
CHANNEL_INSTANCE_URL_TEMPLATE = '/channelinstance/{}'

# client = MongoClient("mongodb+srv://Admin:Pass1234@apidata.lr4ia.mongodb.net/phase3Database?retryWrites=true&w=majority")
# INITIALIZE_DATABASE = client.phase3Database

client = MongoClient("mongodb+srv://Admin:Pass1234@apidata.lr4ia.mongodb.net/phase2Database?retryWrites=true&w=majority")
DATABASE = client.phase2Database

# GLOBAL ARRAYS AND MODEL_FACADE_INSTANCE (should only have 1)
EXERCISES_ARRAY = []
EQUIPMENT_ARRAY = []
CHANNEL_ARRAY = []
MODEL_FACADE_INSTANCE = None


# Flask and view methods for home, models, model instances, and about pages below
# ====================================================================================================================
app = Flask("__name__")
app.url_map.converters['list'] = ListConverter


# homepage
@app.route("/", methods=['GET'])
def index():
    setup()
    global EXERCISES_ARRAY, EQUIPMENT_ARRAY, CHANNEL_ARRAY
    print(EXERCISES_ARRAY)
    return MODEL_FACADE_INSTANCE.render_homepage()


# about page
@app.route("/about", methods=['GET'])
def about():
    return MODEL_FACADE_INSTANCE.render_about_page()


# exercises model page
@app.route("/exercises/<int:pageNumber>/<list:currentArray>/<string:operationUsed>", methods=['GET', 'POST'])
def exercises(pageNumber, currentArray, operationUsed):
    global EXERCISES_ARRAY
    if currentArray[0] == 'INITIALIZE':
        currentArray = EXERCISES_ARRAY

    return MODEL_FACADE_INSTANCE.render_model_page(modelType="exercise",
                                         pageNumber=pageNumber,
                                         flaskRequest=request,
                                         db=DATABASE,
                                         currentArray=currentArray,
                                         operationUsed=operationUsed)


# equipments model page
@app.route("/equipment/<int:pageNumber>/<list:currentArray>/<string:operationUsed>", methods=['GET', 'POST'])
def equipments(pageNumber, currentArray, operationUsed):
    global EQUIPMENT_ARRAY
    if currentArray[0] == 'INITIALIZE':
        currentArray = EQUIPMENT_ARRAY
    return MODEL_FACADE_INSTANCE.render_model_page(modelType="equipment",
                                         pageNumber=pageNumber,
                                         flaskRequest=request,
                                         db=DATABASE,
                                         currentArray=currentArray,
                                         operationUsed=operationUsed)


# channels model page
@app.route("/channels/<int:pageNumber>/<list:currentArray>/<string:operationUsed>", methods=['GET', 'POST'])
def channels(pageNumber, currentArray, operationUsed):
    global CHANNEL_ARRAY
    if currentArray[0] == 'INITIALIZE':
        currentArray = CHANNEL_ARRAY
    return MODEL_FACADE_INSTANCE.render_model_page(modelType="channel",
                                         pageNumber=pageNumber,
                                         flaskRequest=request,
                                         db=DATABASE,
                                         currentArray=currentArray,
                                         operationUsed=operationUsed)

# All view methods for INSTANCE pages are defined below:
# ==================================================================================================================
# exercise instance pages
@app.route(EXERCISE_INSTANCE_URL_TEMPLATE.format('<int:arrayIndex>'), methods=['GET'])
def exercise_instance(arrayIndex):
    return MODEL_FACADE_INSTANCE.render_model_instance_page("exercise", arrayIndex, DATABASE)


# equipment instance pages
@app.route(EQUIPMENT_INSTANCE_URL_TEMPLATE.format('<int:arrayIndex>'), methods=['GET'])
def equipment_instance(arrayIndex):
    return MODEL_FACADE_INSTANCE.render_model_instance_page("equipment", arrayIndex, DATABASE)


# channel instance pages
@app.route(CHANNEL_INSTANCE_URL_TEMPLATE.format('<int:arrayIndex>'), methods=['GET'])
def channel_instance(arrayIndex):
    return MODEL_FACADE_INSTANCE.render_model_instance_page("channel", arrayIndex, DATABASE)


def setup():
    # Ensure main.py has a initialized version of the 3 global model arrays
    global EXERCISES_ARRAY, EQUIPMENT_ARRAY, CHANNEL_ARRAY, MODEL_FACADE_INSTANCE
    MODEL_FACADE_INSTANCE = ModelFacade(DATABASE)
    print(f'In setup(), instance method to get the instance EXERCISE ARRAY: { MODEL_FACADE_INSTANCE.get_exercises_array()}')
    EXERCISES_ARRAY = MODEL_FACADE_INSTANCE.get_exercises_array()
    EQUIPMENT_ARRAY = MODEL_FACADE_INSTANCE.get_equipment_array()
    CHANNEL_ARRAY = MODEL_FACADE_INSTANCE.get_channel_array()


# Start the Flask web-application when main.py file is run
if __name__ == "__main__":
    # ONLY UNCOMMENT THE LINE BELOW IF YOU WANT TO COMPLETELY RE-INITIALIZE OUR MONGODB
    # Array passed should have "exercise", "equipment", "or channel" based on which of them
    # you want to initialize
    # Requires 1-2 minutes to call APIs and setup all 3 collections.
    # ================================================================================
    # MODEL_FACADE_INSTANCE.initialize_clusters(INITIALIZE_DATABASE, ["exercise", "equipment", "channel"])

    # ONLY UNCOMMENT THE LINE BELOW IF YOU WANT TO COMPLETELY CLEAR OUR MONGODB
    # ================================================================================
    # MODEL_FACADE_INSTANCE.clean_database(INITIALIZE_DATABASE)
    app.run(host="localhost", port=8080, debug=True, use_reloader=True)

