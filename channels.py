#kaylee's password: YC5Vmbrvm7FEhlFB
#connection string: mongodb+srv://Kaylee:YC5Vmbrvm7FEhlFB@apidata.lr4ia.mongodb.net/channels?retryWrites=true&w=majority

from googleapiclient.discovery import build
from flask import Flask, render_template, url_for, request, redirect
from collections import defaultdict
from math import ceil
from pymongo import MongoClient

import os
import json
from pprint import pprint

API_KEY = 'AIzaSyBRfo-541cmvNXmnj7sGFkPfsQSgcRWPP4' #kaylee's
SEARCH_ENGINE_ID = '598e742e6c308d255'

class Channel:
    def __init__(self, snippetDict, statisticsDict):
        self.name = snippetDict['channelTitle']
        self.description = snippetDict['description']
        self.thumbnailURL = snippetDict['thumbnails']['high']['url']
        self.subscriberCount = statisticsDict['subscriberCount']
        self.viewCount = statisticsDict['viewCount']
        self.videoCount = statisticsDict['videoCount']

    def toDict():
        return {"name": self.name, "description": self.description, "url": self.thumbnailURL, "subscriberCount": self.subscriberCount, "viewCount": self.viewCount, "videoCount": self.videoCount}

class Exercise:
    def __init__(self, exercise_id, name, description, category, muscles, muscles_secondary, equipment, images, comments):
        self.id = exercise_id
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


def get_json(exercise_URL, category_URL, muscle_URL, equipment_URL, image_URL, comment_URL, data, headers):
    """
    This method gets a response from all URLs needed from the wger REST API, parses it into json, and returns the json
    :return: JSON message
    """
    exercise =  requests.get(url=exercise_URL, data=data, headers=headers).json()
    category = requests.get(url=category_URL, data=data, headers=headers).json()
    muscle = requests.get(url=muscle_URL, data=data, headers=headers).json()
    equipment = requests.get(url=equipment_URL, data=data, headers=headers).json()
    image = requests.get(url=image_URL, data=data, headers=headers).json()
    comment = requests.get(url=comment_URL, data=data, headers=headers).json()
    return exercise, category, muscle, equipment, image, comment

def cleanhtml(raw_html):
    """
    This method takes a raw HTML string and returns a string without the HTML elements
    """
    clean = re.compile('<.*?>')
    clean_text = re.sub(clean, '', raw_html)
    return clean_text

def get_exercises():
    """
    This method makes all API calls to wger and returns an array of Exercise objects to use for Flask.
    :return: array of Exercise objects
    """

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
        if x["name"] and x["description"] and x["category"] and x["equipment"]: # only exercises with complete info (110 exercises)
            exerciseID = x["id"]

            # strip description of html elements
            description  = cleanhtml(x["description"])

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
            for result in image_results:
                if result["exercise"] == exerciseID:
                    images.append(result["image"])
            images.extend(get_images(x["name"]))        

            # get exercise comment using exercise 
            comments = []
            comment_results = comment_data["results"]
            for result in comment_results:
                if result["exercise"] == exerciseID:
                    comments.append(result["comment"])

            exercise = Exercise(exerciseID, x["name"], description, categoryName, muscles_string, sec_muscles_string, equipment_string,
                                images, comments)
            exercisesArray.append(exercise)
    # return exercisesArray

def get_images(search_string):
    """
    This method makes a request to the Google Custom Search API and returns the 10 images in the search result
    """
    url = f"https://customsearch.googleapis.com/customsearch/v1?searchType=image&key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={search_string}"
    data = requests.get(url).json()
    search_items = data.get("items")
    images = []
    if search_items:
        for item in search_items:
            image_link = item["link"]
            images.append(image_link)
    return images    


def setup():
    """
    This method should make all the API calls, parse the JSON responses, and return an array of Channel objects to use for Flask.
    :return: array of Channel objects
    TODO: Eventually we just need to populate a MongoDB database by calling setup() once when we decide on which API responses and channels to keep.
    """
    print("setting up")
    # We will initially store Channel objects in arrays. Can later store in a MongoDB cluster for Phase II.
    # searchTermsArray = ['bicep curl', 'back squat', 'pull-ups']
    client = MongoClient()
    db = client.channels

    searchTermsArray = ['bicep curl', 'squats', 'deadlift workout']

    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"  # set to 0 to enable HTTPS verification

    # Build the API client to access Youtube Data V3 API
    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = "AIzaSyBE-YXbak2UQlYM3hnKuiGoxxlt9VALgCk"
    # DEVELOPER_KEY = 'AIzaSyB_ga1HNh1X3pdONl6VaxQHlgLkFnEC2fk'
    youtube = build(
        api_service_name, api_version, developerKey=DEVELOPER_KEY)

    # Call helper methods to initialize Channel arrays
    for searchItem in searchTermsArray:
        for item in get_youtube_channels(youtube, searchItem):
            chan = Channel(item['snippet'], get_channel_statistics(youtube, item['snippet']['channelId']))
            print(type(chan))
            return

    # Verify our array has been populated with Channel objects
    # for channel in channelArray :
    #     print(channel.name)
    print(type(channelArray))
    return
    # result = db.objects.insert_one(channelArray)
    # print("object inserted!")
    
setup()