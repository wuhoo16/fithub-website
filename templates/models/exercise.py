from templates.models.model import ModelObjInterface


class Exercise(ModelObjInterface):
    def __init__(self, **kwargs):
        self.id = kwargs["exercise_id"]
        self.arrayIndex = kwargs["arrayIndex"]
        self.name = kwargs["name"]
        self.description = kwargs["description"]
        self.category = kwargs["category"]
        self.subcategory = kwargs["subcategory"]
        self.muscles = kwargs["muscles"]
        self.muscles_secondary = kwargs["muscles_secondary"]
        self.equipment = kwargs["equipment"]
        self.images = kwargs["images"]
        self.comments = kwargs["comments"]

    def to_dictionary(self):
        return {
            '_id': self.id,
            'id': self.id,
            'arrayIndex': self.arrayIndex,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'subcategory': self.subcategory,
            'muscles': self.muscles,
            'muscles_secondary': self.muscles_secondary,
            'equipment': self.equipment,
            'images': self.images,
            'comments': self.comments
        }

    def __str__(self):
        return str(self.arrayIndex)