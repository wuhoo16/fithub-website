import math
import os
import re
import requests

from ebaysdk.finding import Connection
from flask import Flask, render_template, request
from googleapiclient.discovery import build
from pymongo import MongoClient

# Global variables definitions
API_KEY = 'AIzaSyB_ga1HNh1X3pdONl6VaxQHlgLkFnEC2fk'  # michelle's
SEARCH_ENGINE_ID = '598e742e6c308d255'

EXERCISE_BLACKLIST = {'Axe Hold', 'Cycling', 'Upper Body', 'Upper External Oblique', 'Chin-ups', 'Wall Pushup'}
EXERCISE_RENAME_DICT = {'Pushups': 'Chest Push-ups', 'Push Ups': 'Push-ups', 'Snach': 'Snatch',
                        "Squat Thrust": "Burpee", 'Thruster': 'Barbell Thruster Squats'}
EXERCISE_SZ_BAR_TYPOS = {'French Press (skullcrusher) SZ-bar', 'Biceps Curls With SZ-bar', 'Upright Row, SZ-bar',
                         'Reverse Bar Curl'}
EXERCISE_GYM_MAT_SET = {'Leg Raises, Lying', 'Side Crunch', 'Superman'}
PLANK_REMOVED_FLAG = False

EQUIPMENT_BLACKLIST = {'BUKA GEARS ARNOLD WEIGHT LIFTING BODYBUILDING BICEP ARM BLASTER EZ BAR CURL ARMS',
                       '9HORN Exercise Mat/Protective Flooring Mats with EVA Foam Interlocking Tiles and'
                       }
EQUIPMENT_IMAGE_MAPPER = {
    'Cast Iron Kettlebell 5, 10, 15, 20, 25, 30 35,40, 45 +some PAIRS(Choose Weight)': "kettlebell_picture_1.jpg",
    'NEW Weider Cast Iron Kettlebell 10, 15, 20, 25, 30 & 35lb Single (Choose Weight)': "kettlebell_picture_2.jpg",
    'POWERT Vinyl Coated Kettlebell for Weight Lifting Workout 5-50LB--Single': "kettlebell_picture_3.jpg",
    'POWERT Competition Kettlebell Coated Cast Steel Weight Lifting Training 10-50LB': "kettlebell_picture_4.jpg",
    'NEW FRAY FITNESS RUBBER HEX DUMBBELLS select-weight 10,15, 20, 25, 30, 35, 40LB': "dumbbell_picture_1.jpg",
    'POWERT HEX Neoprene Coated Colorful Dumbbell Weight Lifting Training--One Pair': "dumbbell_picture_2.jpg",
    'Adjustable Weight Bench Incline Decline Foldable Full Body Workout Gym Exercise': 'bench_picture_1.jpg',
    'Yoga Mats 0.375 inch (10mm) Thick Exercise Gym Mat Non Slip With Carry Straps': "mat_picture_1.png",
    'Extra Thick Non-slip Yoga Mat Pad Exercise Fitness Pilates w/ Strap 72" x 24"': "mat_picture_2.jpg",
    'Thick Yoga Mat Gym Camping Non-Slip Fitness Exercise Pilates Meditation Pad US': "mat_picture_3.jpg"
}
EQUIPMENT_ID_SET = set()

CHANNELS_ID_SET = set()
CHANNELS_TOPICS = {'/m/019_rr': 'Lifestyle', '/m/032tl': 'Fashion', '/m/027x7n': 'Fitness', '/m/02wbm': 'Food',
                   '/m/03glg': 'Hobby', '/m/041xxh': 'Physical attractiveness (Beauty)', '/m/07c1v': 'Technology',
                   '/m/01k8wb': 'Knowledge', '/m/04rlf': 'Music', '/m/02jjt': 'Entertainment',
                   '/m/05qjc': 'Performing Arts',
                   '/m/0kt51': 'Health', '/m/06ntj': 'Sports', '/m/0glt670': 'Hip-Hop Music'}
CHANNELS_BANNER_BLACKLIST = {'Jeremy Ethier', 'Squat University', 'Squat Bench Deadlift',
                             'Diesel Strength Video Library',
                             'The Deadlift Dad', 'Women Chest Workout', "Renshaw's Personal Training", 'James Grage',
                             'Fit Now Official',
                             'Stephi Nguyen', 'Juicy Calves Fitness'}

exercisesArray = []  # declared globally and initialized from our mongoDB the first time the homepage is visited
equipmentArray = []  # declared globally and initialized from our mongoDB the first time the homepage is visited
channelArray = []  # declared globally and initialized from our mongoDB the first time the homepage is visited

EXERCISE_INSTANCE_URL_TEMPLATE = '/exerciseinstance/{}'
EQUIPMENT_INSTANCE_URL_TEMPLATE = '/equipmentinstance/{}'
CHANNEL_INSTANCE_URL_TEMPLATE = '/channelinstance/{}'
EXERCISE_COUNTER = 0
EQUIPMENT_COUNTER = 0
CHANNEL_COUNTER = 0

client = MongoClient(
    "mongodb+srv://Admin:Pass1234@apidata.lr4ia.mongodb.net/phase1Database?retryWrites=true&w=majority")
db = client.phase2Database


# All classes defined below to help store data attributes
# =============================================================================================================================
# Class for exercise object
class Exercise:
    def __init__(self,
                 exercise_id,
                 arrayIndex,
                 name,
                 description,
                 category,
                 subcategory,
                 muscles,
                 muscles_secondary,
                 equipment,
                 images,
                 comments):
        self.id = exercise_id
        self.arrayIndex = arrayIndex
        self.name = name
        self.description = description
        self.category = category
        self.subcategory = subcategory
        self.muscles = muscles
        self.muscles_secondary = muscles_secondary
        self.equipment = equipment
        self.images = images
        self.comments = comments

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
        return self.name


# Class for equipment object
class Equipment:
    def __init__(self,
                 itemId,
                 arrayIndex,
                 title,
                 value,
                 categoryName,
                 location,
                 replacePictureFlag,
                 galleryURL,
                 viewItemURL,
                 equipmentCategory):
        self.id = itemId
        self.arrayIndex = arrayIndex
        self.name = title
        self.price = value
        self.category = categoryName
        self.location = location
        self.replacePictureFlag = replacePictureFlag
        self.picture = galleryURL
        self.linkToItem = viewItemURL
        self.equipmentCategory = equipmentCategory

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


# Class for channel object
class Channel:
    def __init__(self,
                 id,
                 arrayIndex,
                 name,
                 description,
                 thumbnailURL,
                 subscriberCount,
                 viewCount,
                 videoCount,
                 playlist,
                 topicIdCategories,
                 exerciseCategory,
                 unsubscribedTrailer=None,
                 bannerUrl=None,
                 keywords=None,
                 exerciseSubcategory=None):
        self.id = id  # unique channelId string passed in from the JSON response
        self.arrayIndex = arrayIndex
        self.name = name
        self.description = description
        self.thumbnailURL = thumbnailURL
        self.subscriberCount = subscriberCount
        self.viewCount = viewCount
        self.videoCount = videoCount
        self.playlist = playlist
        self.topicIdCategories = topicIdCategories
        self.exerciseCategory = exerciseCategory
        # Optional parameters are initialized below (set to None if not passed)
        self.unsubscribedTrailer = unsubscribedTrailer
        self.bannerUrl = bannerUrl
        self.keywords = keywords
        self.exerciseSubcategory = exerciseSubcategory

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


# All methods to setup of mongoDB remote database is done below.
# Note that 'setup_database()' should only be run ONCE (unless you want to reinitialize remote database)
# ======================================================================================================================
def clean_database():
    """
    Cleans the current phase's database by dropping all 3 model collections
    :return: None
    """
    db.exercises.drop()
    db.equipments.drop()
    db.channels.drop()


def setup_database():
    """
    Setup the remote mongoDB by initializing all 3 model collections back to back.
    :return: None
    """
    initialize_mongoDB_exercises_collection()
    initialize_mongoDB_equipment_collection()
    initialize_mongoDB_channel_collection()


def initialize_mongoDB_exercises_collection():
    """
    This method drops the existing exercises collection, makes all API calls to wger, and initializes the exercise collection
    in the remote mongoDB.
    :return: None
    """
    db.exercises.drop()  # drop the old collection so we initialize a fresh collection

    root_URL = 'https://wger.de/api/v2/'  # add &status=2 to only get approved exercises
    data = '{"key": "value"}'
    headers = {'Accept': 'application/json'}
    response_data = requests.get(url=root_URL, data=data, headers=headers).json()

    exercise_URL = 'https://wger.de/api/v2/exercise/?limit=224&status=2&language=2'  # english & approved exercises: total 224
    category_URL = response_data["exercisecategory"]
    muscle_URL = response_data["muscle"]
    equipment_URL = response_data["equipment"]
    image_URL = 'https://wger.de/api/v2/exerciseimage/?limit=204'
    comment_URL = 'https://wger.de/api/v2/exercisecomment/?limit=113'

    exercise_data, category_data, muscle_data, equipment_data, image_data, comment_data = get_json(exercise_URL,
                                                                                                   category_URL,
                                                                                                   muscle_URL,
                                                                                                   equipment_URL,
                                                                                                   image_URL,
                                                                                                   comment_URL, data,
                                                                                                   headers)
    results = exercise_data["results"]
    for x in results:
        if x["name"] and x["description"] and x["category"] and x["equipment"]:  # only exercises with complete info
            exerciseID = x["id"]

            # strip description of html elements
            description = clean_html(x["description"])

            # get category name using ID
            categoryID = x["category"]
            categoryResults = category_data["results"]
            category_name = ""
            for result in categoryResults:
                if result["id"] == categoryID:
                    category_name = result["name"]
                    break

            # get muscle name using ID
            musclesList = []
            muscles = x["muscles"]
            muscleResults = muscle_data["results"]  # put this line in the get_json function
            for m in muscles:
                for result in muscleResults:
                    if result["id"] == m:
                        musclesList.append(result["name"])  # do we want "is_front" ?
            muscles_string = ", ".join(musclesList)

            # get secondary muscle name using ID
            sec_musclesList = []
            sec_muscles = x["muscles_secondary"]
            for m2 in sec_muscles:
                for result in muscleResults:
                    if result["id"] == m2:
                        sec_musclesList.append(result["name"])  # do we want "is_front" ?
            sec_muscles_string = ", ".join(sec_musclesList)

            # get equipment name using ID
            equipment_list = []
            equipment = x["equipment"]
            equip_results = equipment_data["results"]
            for e in equipment:
                for result in equip_results:
                    if result["id"] == e:
                        equipment_list.append(result["name"])
            equipment_string = ", ".join(equipment_list)

            # get image URL using exercise
            images = []
            image_results = image_data["results"]
            query_template = "{} workout exercise"
            for result in image_results:
                if result["exercise"] == exerciseID:
                    images.append(result["image"])
            images.extend(get_google_images(query_template.format(x["name"])))

            # get exercise comment using exercise
            comments = []
            comment_results = comment_data["results"]
            for result in comment_results:
                if result["exercise"] == exerciseID:
                    comments.append(result["comment"])

            # Initialize subcategory variable. Use the category_name, x["name"], muscles_string, and sec_muscles_string to decide the subcategory. Note only 'Arms' and 'Legs' are broken down into subcategories
            subcategory = None
            if category_name == 'Arms':
                subcategory = return_arms_subcategory(x['name'], muscles_string, sec_muscles_string)
            elif category_name == 'Legs':
                subcategory = return_legs_subcategory(x['name'])

            global EXERCISE_COUNTER
            exercise = Exercise(exerciseID, EXERCISE_COUNTER, x["name"], description, category_name, subcategory, muscles_string,
                                sec_muscles_string, equipment_string,
                                images, comments)

            if exercise.name in EXERCISE_BLACKLIST:
                pass
            elif should_add_exercise(exercise):
                # Fix badly-named exercises
                if exercise.name in EXERCISE_RENAME_DICT.keys():
                    exercise.name = EXERCISE_RENAME_DICT[exercise.name]
                # Fix SZ-Bar/SZ-bar typos for 4 exercise name, description, and equipment attributes
                if exercise.name in EXERCISE_SZ_BAR_TYPOS:
                    fix_SZ_bar_typo(exercise)
                # Make equipment naming consistent across all models ('Gym mat' -> 'Exercise mat')
                if exercise.name in EXERCISE_GYM_MAT_SET:
                    convert_gym_mat_to_exercise_mat(exercise)
                db.exercises.insert_one(exercise.to_dictionary())
                EXERCISE_COUNTER += 1


def initialize_mongoDB_equipment_collection():
    # PREVIOUS SERPSTACK API CODE
    # queryArray = ['Kettlebell', 'Dumbbell', 'Barbell', 'Bench', 'EZ-Bar', 'Exercise mat']
    # URL_FOR_SERPSTACK = "http://api.serpstack.com/search"
    # serpstackRequestArray = create_serpstack_request_params(queryArray, 7)
    # query_template = '{} workout equipment'
    #
    #
    #
    # for param in serpstackRequestArray:
    #     api_result = requests.get(URL_FOR_EBAY, param)
    #     api_result_json = api_result.json()
    #     shopping_results_arr = api_result_json["shopping_results"]
    #
    #     for result in shopping_results_arr:
    #         # Parse JSON response, only keep products that have 'rating' and 'reviews' to prevent KeyError exception
    #         # We also keep an explicit blacklist of products that do not have relevant images
    #         if 'rating' in result.keys() and 'reviews' in result.keys()
    #               and result['title'] not in EQUIPMENT_BLACKLIST:
    #             global equipmentIdCounter
    #             images = get_google_images(query_template.format(result["title"]))
    #             equipmentCategory = param['query']
    #             if len(images) > 0:  # Only keep data if at least 1 image can be found for it
    #                 eq = Equipment(equipmentIdCounter, result["title"], result["price"], result["rating"],
    #                                   result["reviews"], result["seller"],
    #                                   result["snippet"], result["extensions"], images, result["url"],
    #                                   equipmentCategory)
    #                 db.equipments.insert_one(eq.to_dictionary())
    #                 equipmentIdCounter += 1
    """
    This method drops the existing equipments collection, makes all API calls, and initializes the equipments collection
    in the remote mongoDB.
    :return: None
    """
    db.equipments.drop()  # drop the old collection so we initialize a fresh collection
    EBAY_APP_ID = "AndrewWu-IMBDProj-PRD-be64e9f22-1cd7edca"  # Andrew's App ID
    api = Connection(appid=EBAY_APP_ID, config_file=None)
    queryArray = ['Kettlebell', 'Dumbbell', 'Barbell', 'Bench', 'EZ-Bar', 'Exercise mat']
    queryMapper = {'Kettlebell': 'Kettlebells'}

    for query in queryArray:
        queryTermSaved = query
        if query in queryMapper.keys():
            query = queryMapper[query]
        api_result = api.execute('findItemsAdvanced', {
            'keywords': [query],
            'paginationInput': {
                'entriesPerPage': '12',
                'pageNumber': '1'
            }})
        api_result_dict = api_result.dict()
        shopping_results_arr = api_result_dict["searchResult"]["item"]

        for result in shopping_results_arr:
            # May need to add more vars and checks later
            galleryURL = None
            # if 'galleryPlusPictureURL' in result:
            #     galleryURL = result['galleryPlusPictureURL']
            # else:
            if 'galleryURL' in result:
                galleryURL = result['galleryURL']

            if galleryURL is not None:
                # Mark broken images that need to be loaded statically
                replacePictureFlag = False
                if result['title'] in EQUIPMENT_IMAGE_MAPPER:
                    replacePictureFlag = True

                global EQUIPMENT_COUNTER
                eq = Equipment(result['itemId'],
                               EQUIPMENT_COUNTER,
                               result['title'],
                               result['sellingStatus']['convertedCurrentPrice']['value'],
                               result['primaryCategory']['categoryName'], result['location'],
                               replacePictureFlag,
                               galleryURL,
                               result['viewItemURL'],
                               queryTermSaved)
                # Rewrite bad picture URL with picture's filename
                if eq.replacePictureFlag is True:
                    eq.picture = EQUIPMENT_IMAGE_MAPPER[eq.name]

                # Skip equipment entries that are known to have bad titles/images
                if eq.name in EQUIPMENT_BLACKLIST:
                    pass
                # avoid adding duplicate items to our database
                elif eq.id not in EQUIPMENT_ID_SET:
                    db.equipments.insert_one(eq.to_dictionary())
                    EQUIPMENT_ID_SET.add(eq.id)
                    EQUIPMENT_COUNTER += 1


def initialize_mongoDB_channel_collection():
    """
    This method drops old collection, makes all the API calls, parse the JSON responses, and initializes fresh channels collection
    in the remote mongoDB
    :return: None
    """
    db.channels.drop()  # drop the old collection so we initialize a fresh collection

    searchTermsArray = ['Abs', 'Shoulders', 'Bicep', 'Tricep', 'Squats', 'Deadlift', 'Chest', 'Back', 'Calves']
    exerciseCategoryMapper = {
        'Bicep': 'Arms',
        'Tricep': 'Arms',
        'Squats': 'Legs',
        'Deadlift': 'Legs'
    }
    searchTermTemplate = "{} workout exercise"
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"  # set to 0 to enable HTTPS verification

    # Build the API client to access Youtube Data V3 API
    api_service_name = "youtube"
    api_version = "v3"
    # DEVELOPER_KEY = "AIzaSyBE-YXbak2UQlYM3hnKuiGoxxlt9VALgCk"  # Andy's
    DEVELOPER_KEY = 'AIzaSyB_ga1HNh1X3pdONl6VaxQHlgLkFnEC2fk'  # Michelle's
    youtube = build(
        api_service_name, api_version, developerKey=DEVELOPER_KEY)

    # Call helper methods to initialize Channel arrays
    for searchTerm in searchTermsArray:
        for item in execute_youtube_search_API(youtube, searchTermTemplate.format(searchTerm), maxResults=9):
            snippet = item['snippet']
            statistics = execute_channels_statistics_API(youtube, item['snippet']['channelId'])
            contentDetails = execute_channels_contentDetails_API(youtube, item['snippet']['channelId'])
            playlistTags = contentDetails['player']['embedHtml']
            playlistUrl = convert_channels_embeddedUrl(playlistTags)
            playlist = {"title": contentDetails['snippet']['title'],
                        "description": contentDetails['snippet']['description'],
                        "image": contentDetails['snippet']['thumbnails']['high']['url'], "url": playlistUrl}

            topicDetails = execute_channels_topicDetails_API(youtube, item['snippet']['channelId'])
            topicIdCat = convert_channels_ids_categories(convert_channels_topicIds(topicDetails['topicIds']),
                                                         topicDetails['topicCategories'])
            brandingSettings = execute_channels_brandingSettings_API(youtube, item['snippet']['channelId'])

            brandingSettingsKeywords = None
            # brandingSettingsFeaturedUrls = None
            brandingSettingsImage = None
            brandingSettingsTrailer = None
            try:
                brandingSettingsKeywords = convert_channels_keywords(brandingSettings['channel']['keywords'])
            except:
                pass

            # try:
            #     brandingSettingsFeaturedUrls = brandingSettings['channel']['featuredChannelsUrls']
            # except:
            #     pass

            if snippet['channelTitle'] not in CHANNELS_BANNER_BLACKLIST:
                try:
                    brandingSettingsImage = brandingSettings['image']['bannerTvHighImageUrl']
                except:
                    try:
                        brandingSettingsImage = brandingSettings['image']['bannerImageUrl']
                    except:
                        pass

            try:
                trailerTemp = brandingSettings['channel']['unsubscribedTrailer']
                trailerUrl = ""
                try:
                    trailerUrl = convert_channels_embeddedUrl(trailerTemp['player']['embedHtml'])
                except:
                    pass
                brandingSettingsTrailer = {'title': trailerTemp['snippet']['title'],
                                           'description': trailerTemp['snippet']['description'],
                                           'image': trailerTemp['snippet']['thumbnails']['high']['url'],
                                           'tags': trailerTemp['snippet']['tags'],
                                           'viewCount': trailerTemp['statistics']['viewCount'],
                                           'likeCount': trailerTemp['statistics']['likeCount'],
                                           'dislikeCount': trailerTemp['statistics']['dislikeCount'], 'url': trailerUrl}
            except:
                pass

            statisticsSubscriberCount = 0
            try:
                statisticsSubscriberCount = statistics['subscriberCount']
            except:
                pass

            exerciseCategory = searchTerm
            exerciseSubcategory = None
            # If searching a subcategory term, map and save the broader exercise category
            if searchTerm in exerciseCategoryMapper.keys():
                exerciseCategory = exerciseCategoryMapper[searchTerm]
                exerciseSubcategory = searchTerm

            # Construct Channel object with 10 attributes and 4 optional attributes
            global CHANNEL_COUNTER
            channel = Channel(snippet['channelId'],
                              CHANNEL_COUNTER,
                              snippet['channelTitle'],
                              snippet['description'],
                              snippet['thumbnails']['high']['url'],
                              statisticsSubscriberCount,
                              statistics['viewCount'],
                              statistics['videoCount'],
                              playlist,
                              topicIdCat,
                              exerciseCategory,
                              unsubscribedTrailer=brandingSettingsTrailer,
                              bannerUrl=brandingSettingsImage,
                              keywords=brandingSettingsKeywords,
                              exerciseSubcategory=exerciseSubcategory)

            # Only add channel if it is not a duplicate
            if channel.id not in CHANNELS_ID_SET:
                db.channels.insert_one(channel.to_dictionary())
                CHANNELS_ID_SET.add(channel.id)
                CHANNEL_COUNTER += 1


# All methods for reading from the remote mongoDB to initialize our 3 global arrays
# NOTE THAT ANY CHANGES TO THE OBJECT CONSTRUCTORS MUST BE CHANGED HERE TO MATCH!
# ====================================================================================================================
def initialize_exercises_array_from_db():
    exercisesCursor = db.exercises.find()
    for exerciseDocument in exercisesCursor:
        exercisesArray.append(
            Exercise(exerciseDocument['id'],
                     exerciseDocument['arrayIndex'],
                     exerciseDocument['name'],
                     exerciseDocument['description'],
                     exerciseDocument['category'],
                     exerciseDocument['subcategory'],
                     exerciseDocument['muscles'],
                     exerciseDocument['muscles_secondary'],
                     exerciseDocument['equipment'],
                     exerciseDocument['images'],
                     exerciseDocument['comments']))


def initialize_equipment_array_from_db():
    equipmentsCursor = db.equipments.find()
    for equipmentDocument in equipmentsCursor:
        equipmentArray.append(Equipment(equipmentDocument['id'],
                                        equipmentDocument['arrayIndex'],
                                        equipmentDocument['name'],
                                        equipmentDocument['price'],
                                        equipmentDocument['category'],
                                        equipmentDocument['location'],
                                        equipmentDocument['replacePictureFlag'],
                                        equipmentDocument['picture'],
                                        equipmentDocument['linkToItem'],
                                        equipmentDocument['equipmentCategory']))


def initialize_channel_array_from_db():
    channelCursor = db.channels.find()
    for channelDocument in channelCursor:
        channelArray.append(Channel(channelDocument['id'],
                                    channelDocument['arrayIndex'],
                                    channelDocument['name'],
                                    channelDocument['description'],
                                    channelDocument['thumbnailURL'],
                                    channelDocument['subscriberCount'],
                                    channelDocument['viewCount'],
                                    channelDocument['videoCount'],
                                    channelDocument['playlist'],
                                    channelDocument['topicIdCategories'],
                                    channelDocument['exerciseCategory'],
                                    unsubscribedTrailer=channelDocument['unsubscribedTrailer'],
                                    bannerUrl=channelDocument['bannerUrl'],
                                    keywords=channelDocument['keywords'],
                                    exerciseSubcategory=channelDocument['exerciseSubcategory']))


# All 3 methods for getting 2D list of related cross-model instance id's by using the arrayIndex attribute
# By passing the id value of any instance, each method will return a Python list in the format: [[], [], []] where
# <returnedList>[0] will be the list containing all of the related EXERCISE instance objects
# <returnedList>[1] will be the list containing all of the related EQUIPMENT instance objects
# <returnedList>[2] will be the list containing all of the related CHANNEL instance objects
# ====================================================================================================================
def get_related_objects_for_exercise_instance(id):
    """
    Pass in current instance's id to get 2D list of all related instance object id's
    :param id: The current exercise instance object's id attribute
    :return: a 2D list of lists containing all the related instance objects for all 3 model types
    """
    returnList = []
    relatedExercises = []
    relatedEquipments = []
    relatedChannels = []

    # Find the current instance object in the database and store important attributes
    currentExerciseDoc = db.exercises.find_one({'_id': id})
    if currentExerciseDoc:
        category = currentExerciseDoc['category']
        subcategory = currentExerciseDoc['subcategory']  # Note that this can be equal to None
        equipmentCategory = currentExerciseDoc['equipment']

    # Query the exercise collection for all instances matching the current category (and subcategory if it exists)
    if subcategory is None:
        relatedExercisesCursor = db.exercises.find({'category': category})
        for relatedExerciseDoc in relatedExercisesCursor:
            relatedExercises.append(exercisesArray[relatedExerciseDoc['arrayIndex']])
    else:  # subcategory is not None
        relatedExercisesCursor = db.exercises.find({'subcategory': subcategory})
        for relatedExerciseDoc in relatedExercisesCursor:
            relatedExercises.append(exercisesArray[relatedExerciseDoc['arrayIndex']])

    # Query the equipment collection for all instances matching the current equipmentCategory
    relatedEquipmentsCursor = db.equipments.find({'equipmentCategory': equipmentCategory})
    for relatedEquipmentDoc in relatedEquipmentsCursor:
        relatedEquipments.append(equipmentArray[relatedEquipmentDoc['arrayIndex']])

    # Query the channels collection for all instances matching the current category (and subcategory if it exists)
    if subcategory is None:
        relatedChannelsCursor = db.channels.find({'exerciseCategory': category})
        for relatedChannelDoc in relatedChannelsCursor:
            relatedChannels.append(channelArray[relatedChannelDoc['arrayIndex']])
    else:  # subcategory is not None
        relatedChannelsCursor = db.channels.find({'exerciseSubcategory': subcategory})
        for relatedChannelDoc in relatedChannelsCursor:
            relatedChannels.append(channelArray[relatedChannelDoc['arrayIndex']])

    # Combine the 3 inner arrays and return
    returnList.append(relatedExercises)
    returnList.append(relatedEquipments)
    returnList.append(relatedChannels)
    return returnList


def get_related_objects_for_equipment_instance(id):
    """
    Pass in current instance's id to get 2D list of all related instance object id's.
    NOTE THAT WE CURRENTLY USE AN INDIRECT METHOD TO FIND ALL RELATED CHANNELS. Result relevance may vary...
    :param id: The current equipment instance object's id attribute
    :return: a 2D list of lists containing all the related instance objects for all 3 model types
    """
    returnList = []
    relatedExercises = []
    relatedEquipments = []
    relatedChannels = []

    # Find the current instance object in the database and store important attributes
    currentEquipmentDoc = db.equipments.find_one({'_id': id})
    if currentEquipmentDoc:
        equipmentCategory = currentEquipmentDoc['equipmentCategory']

    # Query the exercise collection for all instances that match current equipmentCategory
    relatedExercisesCursor = db.exercises.find({'equipment': equipmentCategory})
    for relatedExerciseDoc in relatedExercisesCursor:
        relatedExercises.append(exercisesArray[relatedExerciseDoc['arrayIndex']])

    # Use the first related exercise object to determine what exercise category/subcategory to use when querying channels collection
    topExerciseDoc = db.exercises.find_one({'_id': relatedExercises[0].id})
    if topExerciseDoc:
        exerciseCategory = topExerciseDoc['category']
        exerciseSubcategory = topExerciseDoc['subcategory']

    # Query the equipment collection for all instances with the same equipmentCategory
    relatedEquipmentsCursor = db.equipments.find({'equipmentCategory': equipmentCategory})
    for relatedEquipmentDoc in relatedEquipmentsCursor:
        relatedEquipments.append(equipmentArray[relatedEquipmentDoc['arrayIndex']])

    # Query the channels collection and find matches using exercise category of the top related exercise in relatedExercises
    if exerciseSubcategory is None:
        relatedChannelsCursor = db.channels.find({'exerciseCategory': exerciseCategory})
        for relatedChannelDoc in relatedChannelsCursor:
            relatedChannels.append(channelArray[relatedChannelDoc['arrayIndex']])
    else:  # exerciseSubcategory is not None
        relatedChannelsCursor = db.channels.find({'exerciseSubcategory': exerciseSubcategory})
        for relatedChannelDoc in relatedChannelsCursor:
            relatedChannels.append(channelArray[relatedChannelDoc['arrayIndex']])

    # Combine the 3 inner arrays and return
    returnList.append(relatedExercises)
    returnList.append(relatedEquipments)
    returnList.append(relatedChannels)
    return returnList


def get_related_objects_for_channel_instance(id):
    """
    Pass in current instance's id to get 2D list of all related instance object id's.
    NOTE THAT WE CURRENTLY USE AN INDIRECT METHOD TO FIND ALL RELATED EQUIPMENT. Result relevance may vary...
    :param id: The current channel instance object's id attribute
    :return: a 2D list of lists containing all the related instance ids for all 3 model types
    """
    returnList = []
    relatedExercises = []
    relatedEquipments = []
    relatedChannels = []

    # Find the current instance object in the database and store important attributes
    currentChannelDoc = db.channels.find_one({'_id': id})
    if currentChannelDoc:
        exerciseCategory = currentChannelDoc['exerciseCategory']
        exerciseSubcategory = currentChannelDoc['exerciseSubcategory']

    # Query the exercise collection for all instances that match current exerciseCategory/Subcategory
    if exerciseSubcategory is None:
        relatedExercisesCursor = db.exercises.find({'category': exerciseCategory})
        for relatedExerciseDoc in relatedExercisesCursor:
            relatedExercises.append(exercisesArray[relatedExerciseDoc['arrayIndex']])
    else:  # exerciseSubcategory is not None
        relatedExercisesCursor = db.exercises.find({'subcategory': exerciseSubcategory})
        for relatedExerciseDoc in relatedExercisesCursor:
            relatedExercises.append(exercisesArray[relatedExerciseDoc['arrayIndex']])

    # Use the first related exercise object to determine what equipmentCategory to use when querying equipments collection
    topExerciseDoc = db.exercises.find_one({'_id': relatedExercises[0].id})
    if topExerciseDoc:
        equipmentCategory = topExerciseDoc['equipment']

    # Query the equipment collection for all instances with the same indirect equipmentCategory
    relatedEquipmentsCursor = db.equipments.find({'equipmentCategory': equipmentCategory})
    for relatedEquipmentDoc in relatedEquipmentsCursor:
        relatedEquipments.append(equipmentArray[relatedEquipmentDoc['arrayIndex']])

    # Query the channels collection and find matches with the current exerciseCategory/Subcategory
    if exerciseSubcategory is None:
        relatedChannelsCursor = db.channels.find({'exerciseCategory': exerciseCategory})
        for relatedChannelDoc in relatedChannelsCursor:
            relatedChannels.append(channelArray[relatedChannelDoc['arrayIndex']])
    else:  # exerciseSubcategory is not None
        relatedChannelsCursor = db.channels.find({'exerciseSubcategory': exerciseSubcategory})
        for relatedChannelDoc in relatedChannelsCursor:
            relatedChannels.append(channelArray[relatedChannelDoc['arrayIndex']])

    # Combine the 3 inner arrays and return
    returnList.append(relatedExercises)
    returnList.append(relatedEquipments)
    returnList.append(relatedChannels)
    return returnList


# All helper methods for creating HTTP requests, cleaning, filtering, or executing APIs defined below
# ======================================================================================================================
def get_json(exercise_URL, category_URL, muscle_URL, equipment_URL, image_URL, comment_URL, data, headers):
    """
    This method gets a response from all URLs needed from the wger REST API, parses it into json, and returns the json
    :return: JSON message
    """
    exercise = requests.get(url=exercise_URL, data=data, headers=headers).json()
    category = requests.get(url=category_URL, data=data, headers=headers).json()
    muscle = requests.get(url=muscle_URL, data=data, headers=headers).json()
    equipment = requests.get(url=equipment_URL, data=data, headers=headers).json()
    image = requests.get(url=image_URL, data=data, headers=headers).json()
    comment = requests.get(url=comment_URL, data=data, headers=headers).json()
    return exercise, category, muscle, equipment, image, comment


def should_add_exercise(exercise):
    """
    Helper function called in the initialize_mongoDB_exercises_collection() method to mark specific exercise duplicates
    that should NOT be added to the database. These can't be eliminated with the simple blacklist due to identical exercise names.
    This method achieves the following rules:
    1.) Blacklists one of the 'Military Press' exercise with Category == Arms
    2.) Blacklists the first of 2 'Plank' exercises using the global PLANK_REMOVED_FLAG
    3.) Blacklist spanish exercise 'Curl su Panca a 45°" using substring.
    :param exercise: an Exercise object that should have all attributes initialized
    :return: Boolean, True if exercise should be added, False otherwise
    """

    if exercise.name == 'Military Press' and exercise.category == 'Arms':
        return False
    elif exercise.name == 'Plank' and PLANK_REMOVED_FLAG is False:
        return False
    elif 'Curl su Panca a ' in exercise.name:
        return False
    else:
        return True


def fix_SZ_bar_typo(exercise):
    """
    Helper function to fix the SZ-Bar and SZ-bar typos for 4 equipment names, descriptions, and equipment attributes.
    :param exercise: Exercise object with name verified to be in the SZ_BAR_TYPO set
    :return: None
    """
    exercise.name = exercise.name.replace('SZ-Bar', 'EZ-Bar')
    exercise.name = exercise.name.replace('SZ-bar', 'EZ-bar')
    exercise.description = exercise.description.replace('SZ-Bar', 'EZ-Bar')
    exercise.description = exercise.description.replace('SZ-bar', 'EZ-bar')
    exercise.equipment = exercise.equipment.replace('SZ-Bar', 'EZ-Bar')
    exercise.equipment = exercise.equipment.replace('SZ-bar', 'EZ-bar')


def convert_gym_mat_to_exercise_mat(exercise):
    """
    Helper function that renames the equipment attribute for 3 exercises from 'equipment = Gym mat' to 'equipment = Exercise mat'.
    To have consistent tags and link instances across models, we need consistent names.
    :param exercise: An exercise object from the EXERCISE_GYM_MAT_SET
    :return: None
    """
    exercise.equipment = 'Exercise mat'


def return_arms_subcategory(exerciseName, muscles_string, sec_muscles_string):
    if 'Bicep' in exerciseName:
        return 'Bicep'
    elif 'Tricep' in exerciseName:
        return 'Tricep'
    else:
        if 'Biceps' in muscles_string:
            return 'Bicep'
        elif 'Triceps' in muscles_string:
            return 'Tricep'
        else:
            if 'Biceps' in sec_muscles_string:
                return 'Bicep'
            elif 'Triceps' in sec_muscles_string:
                return 'Tricep'
            else:  # If exercise fits neither subcategory, return None
                return None


def return_legs_subcategory(exerciseName):
    if 'Squat' in exerciseName:
        return 'Squats'
    elif 'Deadlift' in exerciseName:
        return 'Deadlift'
    else:  # There are 5 specific exercises that don't fall under Squats or Deadlift subcategory... check <https://github.com/UT-SWLab/TeamA13/issues/47> for more details
        return None


def clean_html(raw_html):
    """
    This method takes a raw HTML string and returns a string without the HTML elements
    """
    clean = re.compile('<.*?>')
    clean_text = re.sub(clean, '', raw_html)
    return clean_text


def get_google_images(search_string, file_type=None):
    """
    This method makes a request to the Google Custom Search API and returns the 10 images in the search result as a
    list of strings, where each string represents an image URL. Can pass in additional optional params
    :param search_string: query string that will be searched
    :param file_type: Optional file-type parameter to limit resulting extension types in the result
    :return: List of image URLs
    """
    if file_type is not None:
        url = f"https://customsearch.googleapis.com/customsearch/v1?searchType=image&key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={search_string}&fileType={file_type}"
    else:
        url = f"https://customsearch.googleapis.com/customsearch/v1?searchType=image&key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={search_string}"
    data = requests.get(url).json()
    search_items = data.get("items")
    images = []
    if search_items:
        for item in search_items:
            image_link = item["link"]
            images.append(image_link)
    return images


def create_serpstack_request_params(queryArray, numResults):
    """
    :param queryArray: array of search terms
    :param numResults: limits the number of shopping results per search term
    :return: array of dictionaries, where each dictionary represents the params to pass to SERPSTACK
    """
    serpstackRequestArray = []
    for query in queryArray:
        serpstackRequestArray.append({
            'access_key': '3f69b854db358b9beae52bf6beb5d79f',  # Christopher's API Key
            'query': query,
            'type': 'shopping',
            'num': str(numResults)
        })
    return serpstackRequestArray


def execute_youtube_search_API(youtubeClient, searchTerm, part="snippet", maxResults=3):
    """
    Helper function that calls the Youtube Data API with youtube client and search term to return an array of Channel resources.
    Each channel resource is modeled in the JSON response as a dictionary with 'etag', 'id', 'kind', and 'snippet' keys. The 'snippet' key --> dictionary with 'channelID',
    'channelTitle', 'description', and 'thumbnails' keys.
    :param youtubeClient: Google api client for Youtube that is expected to already be built/authenticated.
    :param searchTerm: The query search term to pass to the youtube search().list API
    :param part: The type of attribute to return. Set to "snippet" by default
    :param maxResults: The max number of results to return. Set to 3 by default
    :return: Array of Channel resources that are returned from querying the searchTerm
    """
    channelSearchRequest = youtubeClient.search().list(
        q=searchTerm,
        part=part,
        maxResults=maxResults,
        type='channel'
    )
    return channelSearchRequest.execute()['items']


def execute_channels_statistics_API(youtubeClient, channelID):
    """
    Call the Youtube Data API with youtube client and channel ID to return 'statistics' dictionary describing that channel.
    :param youtubeClient: Google api client for Youtube that is expected to already be built/authenticated.
    :param channelID: The channel ID of the channel to get statistics of.
    :return: Statistics object with 'viewCount', 'commentCount', 'subscriberCount', 'hiddenSubscriberCount', 'videoCount' keys
    """
    getChannelStatisticsRequest = youtubeClient.channels().list(
        part="statistics",
        id=channelID
    )
    return getChannelStatisticsRequest.execute()['items'][0]['statistics']


def execute_channels_contentDetails_API(youtubeClient, channelID):
    """
    Call the Youtube Data API with youtube client and channel ID to return 'contentDetails' dictionary describing that channel.
    :param youtubeClient: Google api client for Youtube that is expected to already be built/authenticated.
    :param channelID: The channel ID of the channel to get statistics of.
    :return: ContentDetails object with 'relatedPlaylists.uploads' key
    """
    getChannelContentDetailsRequest = youtubeClient.channels().list(
        part="contentDetails",
        id=channelID
    )
    uploadID = getChannelContentDetailsRequest.execute()['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    getPlaylistRequest = youtubeClient.playlists().list(
        part=["snippet", "player"],
        id=uploadID
    )

    return getPlaylistRequest.execute()['items'][0]


def execute_channels_topicDetails_API(youtubeClient, channelID):
    """
    Call the Youtube Data API with youtube client and channel ID to return 'topicDetails' dictionary describing that channel.
    :param youtubeClient: Google api client for Youtube that is expected to already be built/authenticated.
    :param channelID: The channel ID of the channel to get statistics of.
    :return: topicDetails object with 'topicIds[]', 'topicCategories[]' keys
    """
    getChanneltopicDetailsRequest = youtubeClient.channels().list(
        part="topicDetails",
        id=channelID
    )
    return getChanneltopicDetailsRequest.execute()['items'][0]['topicDetails']


def execute_channels_brandingSettings_API(youtubeClient, channelID):
    """
    Call the Youtube Data API with youtube client and channel ID to return 'brandingSettings' dictionary describing that channel.
    :param youtubeClient: Google api client for Youtube that is expected to already be built/authenticated.
    :param channelID: The channel ID of the channel to get statistics of.
    :return: brandingSettings object with 'channel.keywords', 'channel.defaultTab', 'channel.featuredChannelsUrls[]', 'channel.unsubscribedTrailer' keys
    """
    getChannelbrandingSettingsRequest = youtubeClient.channels().list(
        part="brandingSettings",
        id=channelID
    )
    brandingSettings = getChannelbrandingSettingsRequest.execute()['items'][0]['brandingSettings']

    # didn't set up featured channels: ftChannels = brandingSettings['channel']['featuredChannelsUrls'] (MAY DO LATER IF MORE INFO NEEDED) -- channels.list()
    # setting up embedded html
    try:
        videoID = brandingSettings['channel']['unsubscribedTrailer']
        getUnsubscribedTrailerRequest = youtubeClient.videos().list(
            part=["snippet", "player", "statistics"],
            id=videoID
        )

        brandingSettings['channel']['unsubscribedTrailer'] = getUnsubscribedTrailerRequest.execute()['items'][0]
    except:
        pass

    return brandingSettings


def convert_channels_topicIds(ids):
    topic_arr = []
    i = 0
    # ensuring ids topic ids are unique
    while i < len(ids):
        j = i + 1
        while j < len(ids):
            if ids[i] == ids[j]:
                ids.pop(i)
                i -= 1
                j -= 1
                break
            j += 1
        i += 1

    for id in ids:
        if id in CHANNELS_TOPICS:
            topic_arr.append(CHANNELS_TOPICS[id])
        else:
            print("error in topic dictionary (MISSING TOPIC): ")
            print(id)
            topic_arr.append(id)

    return topic_arr


def convert_channels_ids_categories(ids, categories):
    id_cat_arr = []
    found_match_flag = False

    id_dict = {}
    for id in ids:
        id_dict[id.lower()] = id

    for cat in categories:
        temp_cat = cat.replace("https://en.wikipedia.org/wiki/", "")
        temp_cat = temp_cat.replace("(", "")
        temp_cat = temp_cat.replace(")", "")
        temp_cat_arr = temp_cat.split("_")
        temp_cat_arr.append(temp_cat.replace("_", " "))

        for word in temp_cat_arr:
            if word.lower() == "sport":
                word = "sports"

            if word.lower() in id_dict:
                id_cat_arr.append({'topicId': id_dict[word.lower()], 'topicCategory': cat})
                found_match_flag = True
                break

        if not found_match_flag:
            print("DIDNT FIND MATCH W/ ID & CATEGORY")
            print(cat)

    return id_cat_arr


def convert_channels_embeddedUrl(embeddedTag):
    elements = embeddedTag.split(" ")
    url = ""
    for el in elements:
        if el.startswith("src="):
            el = el.replace("src=", "")
            url = el.replace('"', "")
            break
    return url

def convert_channels_keywords(keywords):
    keyword_arr = []
    words = keywords.split(" ")
    for i in range(len(words)):
        if words[i].startswith('"'):
            phrase = ""
            while not words[i].endswith('"'):
                phrase = phrase + words[i] + " "
                i += 1
            print(phrase)
            phrase = phrase + words[i]
            keyword_arr.append(phrase)
        else:
            keyword_arr.append(words[i])

    return keyword_arr


# Flask and view methods for home, models, model instances, and about pages below
# ====================================================================================================================
app = Flask("__name__")


# homepage
@app.route("/", methods=['GET'])
def index():
    # Initialize global arrays from database before starting the web app
    if len(exercisesArray) == 0:
        initialize_exercises_array_from_db()
    if len(equipmentArray) == 0:
        initialize_equipment_array_from_db()
    if len(channelArray) == 0:
        initialize_channel_array_from_db()
    return render_template('homepage.html')


# exercises model page
@app.route("/exercises/<int:page_number>", methods=['GET'])
def exercises(page_number):
    start, end, num_pages = paginate(page_number, exercisesArray)
    return render_template('exercises.html', exercisesArray=exercisesArray, start=start, end=end,
                           page_number=page_number, num_pages=num_pages)


# equipments model page
@app.route("/equipment/<int:page_number>", methods=['GET'])
def equipments(page_number):
    start, end, num_pages = paginate(page_number, equipmentArray)
    return render_template('equipments.html', equipmentArray=equipmentArray, start=start, end=end,
                           page_number=page_number, num_pages=num_pages)


# channels model page
@app.route("/channels/<int:page_number>", methods=['GET'])
def channels(page_number):
    start, end, num_pages = paginate(page_number, channelArray)
    return render_template('channels.html', channelArray=channelArray, start=start, end=end, page_number=page_number,
                           num_pages=num_pages)


# about page
@app.route("/about", methods=['GET'])
def about():
    return render_template('about.html')


# Helper methods for paginating all 3 model pages
# ==================================================================================================================
# Pagination on Model Pages - assumes 9 instances per page
def paginate(page_number, array):
    startIndex = (page_number - 1) * 9
    endIndex = (page_number * 9) - 1
    if endIndex >= len(array):
        endIndex = len(array) - 1
    num_pages = math.ceil(len(array) / 9)
    return startIndex, endIndex, num_pages


# All view methods for INSTANCE pages are defined below:
# ==================================================================================================================
# exercise instance pages
@app.route(EXERCISE_INSTANCE_URL_TEMPLATE.format('<int:arrayIndex>'), methods=['GET'])
def exercise_instance(arrayIndex):
    # Find current exercise instance object
    e = exercisesArray[arrayIndex]
    # Call method to retrieve 2D List of related indices
    relatedObjects = get_related_objects_for_exercise_instance(e.id)
    return render_template('exerciseInstance.html', e=e, relatedObjects=relatedObjects)


# equipment instance pages
@app.route(EQUIPMENT_INSTANCE_URL_TEMPLATE.format('<int:arrayIndex>'), methods=['GET'])
def equipment_instance(arrayIndex):
    # Find current equipment instance object
    eq = equipmentArray[arrayIndex]
    # Call method to retrieve 2D List of related indices
    relatedObjects = get_related_objects_for_equipment_instance(eq.id)
    return render_template('equipmentInstance.html', equipmentObject=eq, relatedObjects=relatedObjects)
    # TODO: replace this line with error handling page (see Google API Client tutorial, the one where you rickrolled the TAs)
    # return render_template('equipmentInstance.html', equipmentObject=equipmentArray[0], equipmentArray=equipmentArray)


# channel instance pages
@app.route(CHANNEL_INSTANCE_URL_TEMPLATE.format('<int:arrayIndex>'), methods=['GET'])
def channel_instance(arrayIndex):
    # Find current channel instance object
    channelObj = channelArray[arrayIndex]
    # Call method to retrieve 2D List of related indices
    relatedObjects = get_related_objects_for_channel_instance(channelObj.id)
    return render_template('channelInstance.html', channelObj=channelObj, relatedObjects=relatedObjects)


# Start the Flask web-application when main.py file is run
if __name__ == "__main__":
    # ONLY UNCOMMENT THE LINE BELOW IF YOU WANT TO COMPLETELY RE-INITIALIZE OUR MONGODB. Requires 1-2 minutes to call APIs and setup all 3 collections.
    # setup_database()

    # UNCOMMENT ONE OF THE FOLLOWING 3 LINES IF YOU WANT TO RE-INITIALIZE A SPECIFIC MODEL'S COLLECTION
    # initialize_mongoDB_exercises_collection()
    # initialize_mongoDB_equipment_collection()
    # initialize_mongoDB_channel_collection()

    app.run(host="localhost", port=8080, debug=True, use_reloader=True)
