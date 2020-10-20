import os
import requests
import re
import math

from googleapiclient.discovery import build
from flask import Flask, render_template, url_for, request, redirect
from pymongo import MongoClient

# Global variables definitions
API_KEY = 'AIzaSyB_ga1HNh1X3pdONl6VaxQHlgLkFnEC2fk' # michelle's
SEARCH_ENGINE_ID = '598e742e6c308d255'
equipmentIdCounter = 1
EXERCISE_BLACKLIST = {'Axe Hold', 'Cycling', 'Upper Body', 'Upper External Oblique', 'Chin-ups', 'Wall Pushup'}
EXERCISE_RENAME_DICT = {'Pushups': 'Chest Push-ups', 'Push Ups': 'Push-ups', 'Snach': 'Snatch', "Squat Thrust": "Burpee", 'Thruster': 'Barbell Thruster Squats'}
EXERCISE_SZ_BAR_TYPOS = {'French Press (skullcrusher) SZ-bar', 'Biceps Curls With SZ-bar', 'Upright Row, SZ-bar', 'Reverse Bar Curl'}
EXERCISE_GYM_MAT_SET = {'Leg Raises, Lying', 'Side Crunch', 'Superman'}
PLANK_REMOVED_FLAG = False
EQUIPMENT_BLACKLIST = {'SML-1 Monster Lite Squat Stand - Made in the USA', 'ETHOS Power Rack 1.0, Red', 'Core Home Fitness Adjustable Dumbbell Set',
                       'Harbinger Pull-Up Bar Black - Hand Exer. Equip. at Academy Sports', 'Fuel Pureformance Xtreme Doorway Gym',
                       'Stamina Doorway Trainer Plus, Black', 'WEIDER Rubber Hex Dumbbell SINGLE 25 lb Pound Weight IN HAND FREE SHIP',
                       'A Pair of Dumbbells Set, Adjustable Free Weights Barbell Set 5-66lb (Black)', 'CAP Rubber Coated Hex Dumbbell 40 lb Weight Lifting Training Home Workout Single',
                       'Harbinger Multi-Gym Sport Pull-Up Bar - Hand Exercise Equipment at Academy Sports', 'Mind Reader - Pull-up bar - black'}
CHANNELS_ID_SET = set()
exercisesArray = []    # declared globally and initialized from our mongoDB the first time the homepage is visited
equipmentArray = []    # declared globally and initialized from our mongoDB the first time the homepage is visited
channelArray = []      # declared globally and initialized from our mongoDB the first time the homepage is visited
client = MongoClient("mongodb+srv://Admin:Pass1234@apidata.lr4ia.mongodb.net/phase1Database?retryWrites=true&w=majority")
db = client.phase2Database


# All classes defined below to help store data attributes
# =============================================================================================================================
# Class for exercise object
class Exercise:
    def __init__(self, exercise_id, name, description, category, subcategory, muscles, muscles_secondary, equipment, images, comments):
        self.id = exercise_id
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
    def __init__(self, id, name, price, rating, reviews, seller, snippet, extensions, images, url, equipmentCategory):
        self.id = id  # unique id generated in the backend to help create dynamic URLs
        self.name = name  # called 'title' in JSON
        self.price = price
        self.rating = rating
        self.reviews = reviews
        self.seller = seller
        self.snippet = snippet
        self.extensions = extensions
        self.images = images
        self.url = url
        self.equipmentCategory = equipmentCategory

    def to_dictionary(self):
        return {
            '_id': self.id,
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'rating': self.rating,
            'reviews': self.reviews,
            'seller': self.seller,
            'snippet': self.snippet,
            'extensions': self.extensions,
            'images': self.images,
            'url': self.url,
            'equipmentCategory': self.equipmentCategory
        }

    def __str__(self):
        return self.name


# Class for channel object
class Channel:
    def __init__(self, channelId, channelTitle, description,  thumbnailURL, subscriberCount, viewCount, videoCount, exerciseCategory, exerciseSubcategory=None):
        self.id = channelId  # unique channelId string passed in from the JSON response
        self.name = channelTitle
        self.description = description
        self.thumbnailURL = thumbnailURL
        self.subscriberCount = subscriberCount
        self.viewCount = viewCount
        self.videoCount = videoCount
        self.exerciseCategory = exerciseCategory
        self.exerciseSubcategory = exerciseSubcategory

    def to_dictionary(self):
        return {
            '_id': self.id,
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'thumbnailURL': self.thumbnailURL,
            'subscriberCount': self.subscriberCount,
            'viewCount': self.viewCount,
            'videoCount': self.videoCount,
            'exerciseCategory': self.exerciseCategory,
            'exerciseSubcategory': self.exerciseSubcategory
        }

    def __str__(self):
        return self.name


# Setup of mongoDB remote database is done below. Note that this should only be run ONCE (unless you want to reinitialize remote database)
# ===========================================================================================================================================
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
    Setup the remote mongoDB by initializing all 3 model collections
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

    exercise_data, category_data, muscle_data, equipment_data, image_data, comment_data = get_json(exercise_URL, category_URL, muscle_URL, equipment_URL, image_URL, comment_URL, data, headers)

    results = exercise_data["results"]
    for x in results:
        if x["name"] and x["description"] and x["category"] and x["equipment"]:  # only exercises with complete info (110 exercises)
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

            exercise = Exercise(exerciseID, x["name"], description, category_name, subcategory, muscles_string, sec_muscles_string, equipment_string,
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


def initialize_mongoDB_equipment_collection():
    """
    This method drops the existing equipments collection, makes all API calls, and initializes the equipments collection
    in the remote mongoDB.
    :return: None
    """
    db.equipments.drop()  # drop the old collection so we initialize a fresh collection

    queryArray = ['Kettlebell', 'Dumbbell', 'Barbell', 'Bench', 'EZ-Bar', 'Exercise mat']
    URL_FOR_SERPSTACK = "http://api.serpstack.com/search"
    serpstackRequestArray = create_serpstack_request_params(queryArray, 7)
    query_template = '{} workout equipment'

    for param in serpstackRequestArray:
        api_result = requests.get(URL_FOR_SERPSTACK, param)
        api_result_json = api_result.json()
        shopping_results_arr = api_result_json["shopping_results"]

        for result in shopping_results_arr:
            # Parse the JSON response and only keep products that have 'rating' and 'reviews' to prevent KeyError exception
            # We also keep an explicit blacklist of products that do not have relevant images
            if 'rating' in result.keys() and 'reviews' in result.keys() and result['title'] not in EQUIPMENT_BLACKLIST:
                global equipmentIdCounter
                images = get_google_images(query_template.format(result["title"]))
                equipmentCategory = param['query']
                if len(images) > 0:  # Only keep data if at least 1 image can be found for it
                    eq = Equipment(equipmentIdCounter, result["title"], result["price"], result["rating"], result["reviews"], result["seller"],
                                   result["snippet"], result["extensions"], images, result["url"], equipmentCategory)
                    db.equipments.insert_one(eq.to_dictionary())
                    equipmentIdCounter += 1


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
    DEVELOPER_KEY = "AIzaSyBE-YXbak2UQlYM3hnKuiGoxxlt9VALgCk"  # Andy's
    # DEVELOPER_KEY = 'AIzaSyB_ga1HNh1X3pdONl6VaxQHlgLkFnEC2fk' # Michelle's
    youtube = build(
        api_service_name, api_version, developerKey=DEVELOPER_KEY)

    # Call helper methods to initialize Channel arrays
    for searchTerm in searchTermsArray:
        for item in execute_youtube_search_API(youtube, searchTermTemplate.format(searchTerm), maxResults=5):
                snippet = item['snippet']
                statistics = execute_channels_statistics_API(youtube, item['snippet']['channelId'])
                exerciseCategory = searchTerm
                exerciseSubcategory = None
                # If searching a subcategory term, map and save the broader exercise category
                if searchTerm in exerciseCategoryMapper.keys():
                    exerciseCategory = exerciseCategoryMapper[searchTerm]
                    exerciseSubcategory = searchTerm

                channel = Channel(snippet['channelId'], snippet['channelTitle'], snippet['description'], snippet['thumbnails']['high']['url'],
                                  statistics['subscriberCount'], statistics['viewCount'], statistics['videoCount'], exerciseCategory, exerciseSubcategory)
                # Only add channel if it is not a duplicate
                if channel.id not in CHANNELS_ID_SET:
                    db.channels.insert_one(channel.to_dictionary())
                    CHANNELS_ID_SET.add(channel.id)


# All helper API-call methods or JSON-parsing helper methods defined below
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
        return 'Biceps'
    elif 'Tricep' in exerciseName:
        return 'Triceps'
    else:
        if 'Biceps' in muscles_string:
            return 'Biceps'
        elif 'Triceps' in muscles_string:
            return 'Triceps'
        else:
            if 'Biceps' in sec_muscles_string:
                return 'Biceps'
            elif 'Triceps' in sec_muscles_string:
                return 'Triceps'
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


# All global array initializations done below
# Note these arrays will serve as a master-list of all instances to help with the model pages
# ==================================================================================================================
def initialize_exercises_array_from_db():
    exercisesCursor = db.exercises.find()
    for exerciseDocument in exercisesCursor:
        exercisesArray.append(Exercise(exerciseDocument['id'], exerciseDocument['name'], exerciseDocument['description'],
                                        exerciseDocument['category'], exerciseDocument['subcategory'], exerciseDocument['muscles'],
                                        exerciseDocument['muscles_secondary'], exerciseDocument['equipment'],
                                        exerciseDocument['images'], exerciseDocument['comments']))


def initialize_equipment_array_from_db():
    equipmentsCursor = db.equipments.find()
    for equipmentDocument in equipmentsCursor:
        equipmentArray.append(Equipment(equipmentDocument['id'], equipmentDocument['name'], equipmentDocument['price'],
                                        equipmentDocument['rating'], equipmentDocument['reviews'],
                                        equipmentDocument['seller'], equipmentDocument['snippet'],
                                        equipmentDocument['extensions'], equipmentDocument['images'],
                                        equipmentDocument['url'], equipmentDocument['equipmentCategory']))


def initialize_channel_array_from_db():
    channelCursor = db.channels.find()
    for channelDocument in channelCursor:
        channelArray.append(Channel(channelDocument['id'], channelDocument['name'], channelDocument['description'],
                                    channelDocument['thumbnailURL'], channelDocument['subscriberCount'],
                                    channelDocument['viewCount'], channelDocument['videoCount'], channelDocument['exerciseCategory'],
                                    channelDocument['exerciseSubcategory']))


# At this point all helper methods definitions and API calls should be done. (Later DB should be populated already)
# Flask infrastructure and view methods for home, models, and about pages
# ==================================================================================================================
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
    return render_template('exercises.html', exercisesArray=exercisesArray, start=start, end=end, page_number=page_number, num_pages=num_pages)


# equipments model page
@app.route("/equipment", methods=['GET'])
def equipments():
    return render_template('equipments.html', equipmentArray=equipmentArray)


# channels model page
@app.route("/channels", methods=['GET'])
def channels():
    return render_template('channels.html', channelArray=channelArray)


# about page
@app.route("/about", methods=['GET'])
def about():
    return render_template('about.html')

# Helper methods for model pages
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
@app.route("/exercises/<int:exercise_id>", methods=['GET'])
def exercise_instance(exercise_id):
    if exercise_id == 345:
        return render_template('exerciseInstance1.html')
    elif exercise_id == 227:
        return render_template('exerciseInstance2.html')
    elif exercise_id == 343:
        return render_template('exerciseInstance3.html')
    else:
        return render_template('exerciseInstance.html', exercise_id=exercise_id, exercisesArray=exercisesArray)


# equipment instance pages
@app.route("/equipments/<int:equipmentID>", methods=['GET'])
def equipment_instance(equipmentID):
    equipmentObject = equipmentArray[equipmentID - 1]
    return render_template('equipmentInstance.html', equipmentObject=equipmentObject)


# channel instance pages
# @app.route("/channels/<string:channelID>", methods=['GET'])
# def channel_instance(channelID):
#     return render_template('channelInstance.html', channelID=channelID, channelArray=channelArray)

@app.route("/channels/<string:channelID>", methods=['GET']) 
def channel_instance(channelID):
    if channelID == "UCb67rmuez0SKOQbZ4vCRDHQ":
        return render_template('channelsInstance1.html')
    elif channelID == "UCZvdYkjBXBSxhosgkWkDyvQ":
        return render_template('channelsInstance2.html')
    elif channelID == "UC_gbQ9J76mYJ5S3zVTANM_w":
        return render_template('channelsInstance3.html')
    else:
        return render_template('channels.html')


# Start the Flask web-application when app.py file is run
if __name__ == "__main__":
    # ONLY UNCOMMENT THE LINE BELOW IF YOU WANT TO COMPLETELY RE-INITIALIZE OUR MONGODB. Requires 1-2 minutes to call APIs and setup all 3 collections.
    # setup_database()

    # UNCOMMENT ONE OF THE FOLLOWING 3 LINES IF YOU WANT TO RE-INITIALIZE A SPECIFIC MODEL'S COLLECTION
    # initialize_mongoDB_exercises_collection()
    # initialize_mongoDB_equipment_collection()
    # initialize_mongoDB_channel_collection()

    app.run(host="localhost", port=8080, debug=True, use_reloader=True)

