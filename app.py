import os
import json
import requests
import pprint as pp

from googleapiclient.discovery import build
from flask import Flask, render_template, url_for, request, redirect
from collections import defaultdict
from math import ceil


class Channel:
    def __init__(self, snippetDict, statisticsDict):
        self.name = snippetDict['channelTitle']
        self.description = snippetDict['description']
        self.thumbnailURL = snippetDict['thumbnails']['high']['url']
        self.subscriberCount = statisticsDict['subscriberCount']
        self.viewCount = statisticsDict['viewCount']
        self.videoCount = statisticsDict['videoCount']

class Exercise:
    def __init__(self, name, description, category, muscles, muscles_secondary, equipment, images, comments):
        self.name = name
        self.description = description
        self.category = category
        self.muscles = muscles
        self.muscles_secondary = muscles_secondary
        self.equipment = equipment
        self.images = images
        self.comments = comments


def get_youtube_channels(youtubeClient, searchTerm, part="snippet", maxResults=3):
    """
    Call the Youtube Data API with youtube client and search term to return an array of Channel resources. Each channel resource is modeled in the
    JSON response as a dictionary with 'etag', 'id', 'kind', and 'snippet' keys. The 'snippet' key --> dictionary with 'channelID',
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


def get_channel_statistics(youtubeClient, channelID):
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


def get_json(url, data, headers):
    response = requests.get(url=url, data=data, headers=headers)
    return response.json()


def get_exercises():
    exerciseArray = []

    root_URL = 'https://wger.de/api/v2/'  # add &status=2 to only get approved exercises
    data = '{"key": "value"}'
    headers = {'Accept': 'application/json'}
    response = requests.get(url=root_URL, data=data, headers=headers)
    response_data = response.json()

    # exercise_URL = response_data["exercise"]
    # exercise_URL = 'https://wger.de/api/v2/exercise/?limit=100'
    exercise_URL = 'https://wger.de/api/v2/exercise/?limit=224&status=2&language=2'  # english, approved exercises: total 224
    category_URL = response_data["exercisecategory"]
    muscle_URL = response_data["muscle"]
    equipment_URL = response_data["equipment"]
    # image_URL = response_data["exerciseimage"]
    image_URL = 'https://wger.de/api/v2/exerciseimage/?limit=204'
    # comment_URL = response_data["exercisecomment"]
    comment_URL = 'https://wger.de/api/v2/exercisecomment/?limit=113'

    exercise_data = get_json(exercise_URL, data, headers)
    category_data = get_json(category_URL, data, headers)
    muscle_data = get_json(muscle_URL, data, headers)
    equipment_data = get_json(equipment_URL, data, headers)
    image_data = get_json(image_URL, data, headers)
    comment_data = get_json(comment_URL, data, headers)

    nextURL = exercise_data["next"]
    results = exercise_data["results"]
    for x in results:
        exerciseID = x["id"]

        # get category name using ID
        categoryID = x["category"]
        categoryResults = category_data["results"]
        categoryName = ""
        for result in categoryResults:
            if result["id"] == categoryID:
                categoryName = result["name"]
                break

        # get muscle name using ID
        musclesList = []
        muscles = x["muscles"]
        muscleResults = muscle_data["results"]  # put this line in the get_json function
        for m in muscles:
            for result in muscleResults:
                if result["id"] == m:
                    musclesList.append(result["name"])  # do we want "is_front" ?

        # get secondary muscle name using ID
        sec_musclesList = []
        sec_muscles = x["muscles_secondary"]
        for m2 in sec_muscles:
            for result in muscleResults:
                if result["id"] == m2:
                    sec_musclesList.append(result["name"])  # do we want "is_front" ?

        # get equipment name using ID
        equipment_list = []
        equipment = x["equipment"]
        equip_results = equipment_data["results"]
        for e in equipment:
            for result in equip_results:
                if result["id"] == e:
                    equipment_list.append(result["name"])

        # get image URL using exercise # (if exists) -----> need to go through all exercise images list *********
        images = []  # list of image URLs --------> save image in db instead of going to website?
        image_results = image_data["results"]
        for result in image_results:
            if result["exercise"] == exerciseID:
                images.append(result["image"])

        # get exercise comment using exercise # (if exists)
        comments = []  # list of image URLs --------> save image in db instead of going to website?
        comment_results = comment_data["results"]
        for result in comment_results:
            if result["exercise"] == exerciseID:
                comments.append(result["comment"])

        exercise = Exercise(x["name"], x["description"], categoryName, musclesList, sec_musclesList, equipment_list,
                            images, comments)
        exerciseArray.append(exercise)
        # pp(exercise)
    return exerciseArray


def setup():
    """
    This method should make all the API calls, parse the JSON responses, and return an array of Channel objects to use for Flask.
    :return: array of Channel objects
    TODO: Eventually we just need to populate a MongoDB database by calling setup() once when we decide on which API responses and channels to keep.
    """
    # We will initially store Channel objects in arrays. Can later store in a MongoDB cluster for Phase II.
    searchTermsArray = ['bicep curl', 'back squat', 'pull-ups']
    channelArray = []

    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"  # set to 0 to enable HTTPS verification

    # Build the API client to access Youtube Data V3 API
    api_service_name = "youtube"
    api_version = "v3"
    # DEVELOPER_KEY = "AIzaSyBE-YXbak2UQlYM3hnKuiGoxxlt9VALgCk"
    DEVELOPER_KEY = 'AIzaSyB_ga1HNh1X3pdONl6VaxQHlgLkFnEC2fk'
    youtube = build(
        api_service_name, api_version, developerKey=DEVELOPER_KEY)

    # Call helper methods to initialize Channel arrays
    for item in get_youtube_channels(youtube, 'bicep curl'):
        channelArray.append(Channel(item['snippet'], get_channel_statistics(youtube, item['snippet']['channelId'])))

    for item in get_youtube_channels(youtube, 'squats'):
        channelArray.append(Channel(item['snippet'], get_channel_statistics(youtube, item['snippet']['channelId'])))

    for item in get_youtube_channels(youtube, 'deadlift workout'):
        channelArray.append(Channel(item['snippet'], get_channel_statistics(youtube, item['snippet']['channelId'])))

    # Verify our array has been populated with Channel objects
    # for channel in channelArray :
    #     print(channel.name)
    return channelArray


# After initializing our arrays with data from the Youtube API calls, we setup our flask infrastructure
app = Flask("__name__")


# homepage
@app.route("/", methods=['GET'])
def index():
    return render_template('homepage.html')


# channels model page
@app.route("/exercises", methods=['GET'])
def exercises():
    exercisesArray = get_exercises()
    return render_template('exercises.html', exercisesArray=exercisesArray)


# equipment model page <TODO: GET THE PYTHON API METHOD AND HTML FILE FROM CHRISTOPHER's branch>
@app.route("/equipment", methods=['GET'])
def equipments():
    # equipmentArray = get_equipments()
    # return render_template('equipments.html', equipmentArray=equipmentArray)
    return render_template('equipments.html')


# channels model page
@app.route("/channels", methods=['GET'])
def channels():
    channelArray = setup()
    return render_template('channels.html', channelArray=channelArray)


# about page
@app.route("/about", methods=['GET'])
def about():
    channelArray = setup()
    return render_template('about.html', channelArray=channelArray)


# All view methods for instance pages are defined below:
# ======================================================================================================
# channel instance pages
@app.route("/channels/<string:channelName>", methods=['GET'])
def channels_instance(channelName):
    return render_template('channelsInstance.html', channelName=channelName)


if __name__ == "__main__":
    app.run(port=8080, debug=True, use_reloader=True)

