from flask import Flask, request
from pymongo import MongoClient

from model_facade import ModelFacade

EXERCISE_INSTANCE_URL_TEMPLATE = '/exerciseinstance/{}'
EQUIPMENT_INSTANCE_URL_TEMPLATE = '/equipmentinstance/{}'
CHANNEL_INSTANCE_URL_TEMPLATE = '/channelinstance/{}'

client = MongoClient("mongodb+srv://Admin:Pass1234@apidata.lr4ia.mongodb.net/phase3Database?retryWrites=true&w=majority")
INITIALIZE_DATABASE = client.phase3Database

client = MongoClient("mongodb+srv://Admin:Pass1234@apidata.lr4ia.mongodb.net/phase2Database?retryWrites=true&w=majority")
DATABASE = client.phase2Database

# Flask and view methods for home, models, model instances, and about pages below
# ====================================================================================================================
app = Flask("__name__")

# homepage
@app.route("/", methods=['GET'])
def index():
    return ModelFacade.render_homepage(DATABASE)  


# about page
@app.route("/about", methods=['GET'])
def about():
    return ModelFacade.render_about_page()


# exercises model page
@app.route("/exercises/<int:page_number>", methods=['GET', 'POST'])
def exercises(page_number):
    return ModelFacade.render_model_page("exercise", page_number, request, DATABASE)


# equipments model page
@app.route("/equipment/<int:page_number>", methods=['GET', 'POST'])
def equipments(page_number):
    return ModelFacade.render_model_page("equipment", page_number, request, DATABASE)


# channels model page
@app.route("/channels/<int:page_number>", methods=['GET', 'POST'])
def channels(page_number):
    return ModelFacade.render_model_page("channel", page_number, request, DATABASE)


# All view methods for INSTANCE pages are defined below:
# ==================================================================================================================
# exercise instance pages
@app.route(EXERCISE_INSTANCE_URL_TEMPLATE.format('<int:arrayIndex>'), methods=['GET'])
def exercise_instance(arrayIndex):
    return ModelFacade.render_model_instance_page("exercise", arrayIndex, DATABASE)


# equipment instance pages
@app.route(EQUIPMENT_INSTANCE_URL_TEMPLATE.format('<int:arrayIndex>'), methods=['GET'])
def equipment_instance(arrayIndex):
    return ModelFacade.render_model_instance_page("equipment", arrayIndex, DATABASE)


# channel instance pages
@app.route(CHANNEL_INSTANCE_URL_TEMPLATE.format('<int:arrayIndex>'), methods=['GET'])
def channel_instance(arrayIndex):
    return ModelFacade.render_model_instance_page("channel", arrayIndex, DATABASE)


# Start the Flask web-application when main.py file is run
if __name__ == "__main__":
    # ONLY UNCOMMENT THE LINE BELOW IF YOU WANT TO COMPLETELY RE-INITIALIZE OUR MONGODB
    # Array passed should have "exercise", "equipment", "or channel" based on which of them
    # you want to initialize
    # Requires 1-2 minutes to call APIs and setup all 3 collections.
    # ================================================================================
    # ModelFacade.initialize_clusters(INITIALIZE_DATABASE, ["exercise", "equipment", "channel"])

    # ONLY UNCOMMENT THE LINE BELOW IF YOU WANT TO COMPLETELY CLEAR OUR MONGODB
    # ================================================================================
    # ModelFacade.clean_database(INITIALIZE_DATABASE)

    app.run(host="localhost", port=8080, debug=True, use_reloader=True)
