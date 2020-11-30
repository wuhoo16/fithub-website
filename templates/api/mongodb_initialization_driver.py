from pymongo import MongoClient
from templates.api.exercise_api import ExerciseAPI
from templates.api.equipment_api import EquipmentAPI
from templates.api.channel_api import ChannelAPI

client = MongoClient("mongodb+srv://Admin:Pass1234@apidata.lr4ia.mongodb.net/phase3Database?retryWrites=true&w=majority")
DATABASE = client.phase3Database


# All methods to setup of mongoDB remote database is done below.
# Note that 'setup_database()' should only be run ONCE (unless you want to reinitialize remote database)
# ======================================================================================================================
def clean_database(db):
    """
    Cleans the current phase's database by dropping all 3 model collections
    :param db: The mongo database to add the collection to
    :return: None
    """
    db.exercises.drop()
    db.equipments.drop()
    db.channels.drop()


def setup_database(db, modelType=None):
    """
    Setup the remote mongoDB by initializing all the model collections passed into args argument. Note that if the 2nd parameter
    is not provided, this method will initialize all 3 collections by default.
    :param db: The mongo database to add the collection to
    :param modelType: Optional parameter to only initialize one model collection. Expects one of the following strings: 'exercises', 'equipments', 'channels'
    :return: None
    """
    if modelType is None:
        ExerciseAPI.initialize_mongoDB_collection(db)
        EquipmentAPI.initialize_mongoDB_collection(db)
        ChannelAPI.initialize_mongoDB_collection(db)
    else:
        if modelType == "exercises":
            ExerciseAPI.initialize_mongoDB_collection(db)
        elif modelType == "equipments":
            EquipmentAPI.initialize_mongoDB_collection(db)
        elif modelType == "channels":
            ChannelAPI.initialize_mongoDB_collection(db)
        else:
            raise NameError("ERROR: " + modelType + " is not a valid model type! "
                                                    "Only 'exercises', 'equipments', or 'channels' are supported parameters to pass in.")


if __name__ == "__main__":
    # ONLY UNCOMMENT THE LINE BELOW IF YOU WANT TO COMPLETELY RE-INITIALIZE ALL 3 MODEL COLLECTIONS IN OUR MONGODB. Requires 1-2 minutes to call APIs and setup all 3 collections.
    # ==============================================================================================================================================================================
    # setup_database(DATABASE)

    # UNCOMMENT ONE OF THE FOLLOWING 3 LINES IF YOU WANT TO RE-INITIALIZE A SPECIFIC MODEL COLLECTION IN OUR MONGODB
    # ================================================================================================================
    # ExerciseAPI.initialize_mongoDB_collection(DATABASE)
    # EquipmentAPI.initialize_mongoDB_collection(DATABASE)
    # ChannelAPI.initialize_mongoDB_collection(DATABASE)

    # ONLY UNCOMMENT THE LINE BELOW IF YOU WANT TO COMPLETELY DROP ALL 3 MONGODB COLLECTIONS
    # =========================================================================================
    # clean_database(INITIALIZE_DATABASE)
    pass

