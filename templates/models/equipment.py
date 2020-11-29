from templates.models.model import ModelObjInterface

class Equipment(ModelObjInterface):
    def __init__(self, **kwargs):
        self.id = kwargs["itemId"]
        self.arrayIndex = kwargs["arrayIndex"]
        self.name = kwargs["title"]
        self.price = kwargs["value"]
        self.category = kwargs["categoryName"]
        self.location = kwargs["location"]
        self.replacePictureFlag = kwargs["replacePictureFlag"]
        self.picture = kwargs["galleryURL"]
        self.linkToItem = kwargs["viewItemURL"]
        self.equipmentCategory = kwargs["equipmentCategory"]


    def to_dictionary(self):
        return {
            '_id': self.id,
            'id': self.id,
            'arrayIndex': self.arrayIndex,
            'name': self.name,
            'price': self.price,
            'category': self.category,
            'location': self.location,
            'replacePictureFlag': self.replacePictureFlag,
            'picture': self.picture,
            'linkToItem': self.linkToItem,
            'equipmentCategory': self.equipmentCategory
        }


    def __str__(self):
        return self.name