class Channel():
    def __init__(self, **kwargs):
        self.id = kwargs["id"]  # unique channelId string passed in from the JSON response
        self.arrayIndex = kwargs["arrayIndex"]
        self.name = kwargs["name"]
        self.description = kwargs["description"]
        self.thumbnailURL = kwargs["thumbnailURL"]
        self.subscriberCount = kwargs["subscriberCount"]
        self.viewCount = kwargs["viewCount"]
        self.videoCount = kwargs["videoCount"]
        self.playlist = kwargs["playlist"]
        self.topicIdCategories = kwargs["topicIdCategories"]
        self.exerciseCategory = kwargs["exerciseCategory"]
        # Optional parameters are initialized below (set to None if not passed)
        self.unsubscribedTrailer = kwargs["unsubscribedTrailer"]
        self.bannerUrl = kwargs["bannerUrl"]
        self.keywords = kwargs["keywords"]
        self.exerciseSubcategory = kwargs["exerciseSubcategory"]


    def to_dictionary(self):
        return {
            '_id': self.id,
            'id': self.id,
            'arrayIndex': self.arrayIndex,
            'name': self.name,
            'description': self.description,
            'thumbnailURL': self.thumbnailURL,
            'subscriberCount': self.subscriberCount,
            'viewCount': self.viewCount,
            'videoCount': self.videoCount,
            'playlist': self.playlist,
            'topicIdCategories': self.topicIdCategories,
            'exerciseCategory': self.exerciseCategory,
            'unsubscribedTrailer': self.unsubscribedTrailer,
            'bannerUrl': self.bannerUrl,
            'keywords': self.keywords,
            'exerciseSubcategory': self.exerciseSubcategory
        }


    def __str__(self):
        return self.name