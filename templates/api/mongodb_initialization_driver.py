from pymongo import MongoClient

# DO NOT REMOVE THIS IMPORT, IT IS REQUIRED IF YOU WANT TO SETUP DATABASE
from model_facade import ModelFacade

# MongoDB Variables
client = MongoClient(System.getenv("MONGODB_URI")
DATABASE = client.phase4Database

if __name__ == "__main__":
    # ONLY UNCOMMENT THE LINE BELOW IF YOU WANT TO COMPLETELY RE-INITIALIZE ALL 3 MODEL COLLECTIONS IN OUR MONGODB. Requires 1-2 minutes to call APIs and setup all 3 collections.
    # ==============================================================================================================================================================================
    # ModelFacade.setup_database(DATABASE)

    # UNCOMMENT ONE OF THE FOLLOWING 3 LINES IF YOU WANT TO RE-INITIALIZE A SPECIFIC MODEL COLLECTION IN OUR MONGODB
    # ================================================================================================================
    # ModelFacade.setup_database(DATABASE, modelType='exercises')
    # ModelFacade.setup_database(DATABASE, modelType='equipments')
    # ModelFacade.setup_database(DATABASE, modelType='channels')

    # ONLY UNCOMMENT THE LINE BELOW IF YOU WANT TO COMPLETELY DROP ALL 3 MONGODB COLLECTIONS
    # =========================================================================================
    # ModelFacade.clean_database(DATABASE)
    pass

