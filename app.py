import os
import pprint as pp

from googleapiclient.discovery import build
from flask import Flask, render_template, request


class Channel:
    def __init__(self, snippetDict, statisticsDict):
        self.name = snippetDict['channelTitle']
        self.description = snippetDict['description']
        self.thumbnailURL = snippetDict['thumbnails']['high']['url']
        self.subscriberCount = statisticsDict['subscriberCount']
        self.viewCount = statisticsDict['viewCount']
        self.videoCount = statisticsDict['videoCount']


def get_youtube_channels(youtubeClient, searchTerm, part="snippet", maxResults=5):
    """
    Call the Youtube Data API with youtube client and search term to return an array of Channel resources. Each channel resource is modeled in the
    JSON response as a dictionary with 'etag', 'id', 'kind', and 'snippet' keys. The 'snippet' key --> dictionary with 'channelID',
    'channelTitle', 'description', and 'thumbnails' keys.

    :param youtubeClient: Google api client for Youtube that is expected to already be built/authenticated.
    :param searchTerm: The query search term to pass to the youtube search().list API
    :param part: The type of attribute to return. Set to "snippet" by default
    :param maxResults: The max number of results to return. Set to 5 by default
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


def setup():
    """
    This method should make all the API calls, parse the JSON responses, and return an array of Channel objects to use for Flask.
    :return: array of Channel objects TODO, we can change this to a dict of excercise --> array of Channel objects when we scale up
    """
    # We will initially store Channel objects in arrays. Can later store in a MongoDB cluster for Phase II.
    searchTermsArray = ['bicep curl', 'back squat', 'deadlift', 'pull-ups', 'military-press', 'treadmill run']
    bicepCurlChannelArray = []

    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"  # set to 0 to enable HTTPS verification

    # Build the API client to access Youtube Data V3 API
    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = "AIzaSyBE-YXbak2UQlYM3hnKuiGoxxlt9VALgCk"
    youtube = build(
        api_service_name, api_version, developerKey=DEVELOPER_KEY)

    # Call helper methods to initialize Channel arrays
    for item in get_youtube_channels(youtube, 'bicep curl'):
        bicepCurlChannelArray.append(Channel(item['snippet'], get_channel_statistics(youtube, item['snippet']['channelId'])))

    # Verify our array has been populated with Channel objects
    # for channel in bicepCurlChannelArray:
    #     print(channel.name)
    return bicepCurlChannelArray


# After initializing our arrays with data from the Youtube API calls, we setup our flask infrastructure
app = Flask("__name__")


@app.route("/")
def index():
    channelArray = setup()
    return render_template('channelModel.html', channelArray=channelArray)


if __name__ == "__main__":
    app.run(port=8080, debug=True, use_reloader=True)

