class APIInterface:
    def __init__(self, **kwargs):
        pass

    def to_dictionary(self): 
        """Returns a dictionary"""
        pass

    def __str__(self):
        """Returns a string"""
        pass

    def initialize_mongoDB_collection(db):
        """
        This method drops the existing model collection, makes all API calls, and initializes the model collection
        in the remote mongoDB.
        :param db: The mongo database to add the collection to
        :return: None
        """
        pass