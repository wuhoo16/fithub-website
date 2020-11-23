from pymongo import MongoClient

from exercise_api import Exercise
from equipment_api import Equipment
from channel_api import Channel

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


def setup_database(db):
    """
    Setup the remote mongoDB by initializing all 3 model collections back to back.
    :return: None
    """
    Exercise.initialize_mongoDB_collection(DATABASE)
    Equipment.initialize_mongoDB_collection(DATABASE)
    Channel.initialize_mongoDB_collection(DATABASE)


if __name__ == "__main__":
    # ONLY UNCOMMENT THE LINE BELOW IF YOU WANT TO COMPLETELY RE-INITIALIZE OUR MONGODB. Requires 1-2 minutes to call APIs and setup all 3 collections.
    # setup_database(DATABASE)

    # UNCOMMENT ONE OF THE FOLLOWING 3 LINES IF YOU WANT TO RE-INITIALIZE A SPECIFIC MODEL'S COLLECTION
    # Exercise.initialize_mongoDB_collection(DATABASE)
    # Equipment.initialize_mongoDB_collection(DATABASE)
    # Channel.initialize_mongoDB_collection(DATABASE)

