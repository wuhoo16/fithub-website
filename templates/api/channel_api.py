from templates.api.api_interface import APIInterface
from ..channel import Channel
from googleapiclient.discovery import build
import os

ID_SET = set()
TOPICS = {'/m/019_rr': 'Lifestyle', '/m/032tl': 'Fashion', '/m/027x7n': 'Fitness', '/m/02wbm': 'Food',
                '/m/03glg': 'Hobby', '/m/041xxh': 'Physical attractiveness (Beauty)', '/m/07c1v': 'Technology',
                '/m/01k8wb': 'Knowledge', '/m/04rlf': 'Music', '/m/02jjt': 'Entertainment', '/m/06ntj': 'Sports',
                '/m/05qjc': 'Performing Arts', '/m/02vxn': 'Movies', '/m/0kt51': 'Health', '/m/0glt670': 'Hip-Hop Music'}
BANNER_BLACKLIST = {'Jeremy Ethier', 'Squat University', 'Squat Bench Deadlift',
                            'Diesel Strength Video Library',
                            'The Deadlift Dad', 'Women Chest Workout', "Renshaw's Personal Training", 'James Grage',
                            'Fit Now Official',
                            'Stephi Nguyen', 'Juicy Calves Fitness'}


class ChannelAPI(APIInterface):
    def initialize_mongoDB_collection(db):
        db.channels.drop()  # drop the old collection so we initialize a fresh collection

        channel_counter = 0
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
        # DEVELOPER_KEY = 'AIzaSyB_ga1HNh1X3pdONl6VaxQHlgLkFnEC2fk'  # Michelle's
        youtube = build(
            api_service_name, api_version, developerKey=DEVELOPER_KEY)

        # Call helper methods to initialize Channel arrays
        for searchTerm in searchTermsArray:
            for item in execute_youtube_search_API(youtube, searchTermTemplate.format(searchTerm), maxResults=9):
                snippet = item['snippet']
                statistics = execute_statistics_API(youtube, item['snippet']['channelId'])
                contentDetails = execute_content_details_API(youtube, item['snippet']['channelId'])
                playlistTags = contentDetails['player']['embedHtml']
                playlistUrl = convert_embedded_URL(playlistTags)
                playlist = {"title": contentDetails['snippet']['title'],
                            "description": contentDetails['snippet']['description'],
                            "image": contentDetails['snippet']['thumbnails']['high']['url'], "url": playlistUrl}

                topicDetails = execute_topic_details_API(youtube, item['snippet']['channelId'])
                if topicDetails is None: continue        

                topicIdCat = convert_ids_categories(convert_topic_ids(topicDetails['topicIds']),
                                                            topicDetails['topicCategories'])
                brandingSettings = execute_branding_settings_API(youtube, item['snippet']['channelId'])

                brandingSettingsKeywords = None
                brandingSettingsImage = None
                brandingSettingsTrailer = None
                try:
                    brandingSettingsKeywords = convert_keywords(brandingSettings['channel']['keywords'])
                except:
                    pass

                if snippet['channelTitle'] not in BANNER_BLACKLIST:
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
                        trailerUrl = convert_embedded_URL(trailerTemp['player']['embedHtml'])
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
                channel = Channel(**{
                    "id": snippet['channelId'],
                    "arrayIndex": channel_counter,
                    "name": snippet['channelTitle'],
                    "description": snippet['description'],
                    "thumbnailURL": snippet['thumbnails']['high']['url'],
                    "subscriberCount": int(statisticsSubscriberCount),
                    "viewCount": int(statistics['viewCount']),
                    "videoCount": int(statistics['videoCount']),
                    "playlist": playlist,
                    "topicIdCategories": topicIdCat,
                    "exerciseCategory": exerciseCategory,
                    "unsubscribedTrailer": brandingSettingsTrailer,
                    "bannerUrl": brandingSettingsImage,
                    "keywords": brandingSettingsKeywords,
                    "exerciseSubcategory": exerciseSubcategory
                })

                # Only add channel if it is not a duplicate
                if channel.id not in ID_SET:
                    db.channels.insert_one(channel.to_dictionary())
                    ID_SET.add(channel.id)
                    channel_counter += 1


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


def execute_statistics_API(youtubeClient, channelID):
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


def execute_content_details_API(youtubeClient, channelID):
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


def execute_topic_details_API(youtubeClient, channelID):
    """
    Call the Youtube Data API with youtube client and channel ID to return 'topicDetails' dictionary describing that channel.
    :param youtubeClient: Google api client for Youtube that is expected to already be built/authenticated.
    :param channelID: The channel ID of the channel to get statistics of.
    :return: topicDetails object with 'topicIds[]', 'topicCategories[]' keys
    """
    getChannelTopicDetailsRequest = youtubeClient.channels().list(
        part="topicDetails",
        id=channelID
    )

    try:
        return getChannelTopicDetailsRequest.execute()['items'][0]['topicDetails']
    except KeyError:
        return None


def execute_branding_settings_API(youtubeClient, channelID):
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


def convert_topic_ids(ids):
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
        if id in TOPICS:
            topic_arr.append(TOPICS[id])
        else:
            print("error in topic dictionary (MISSING TOPIC): ")
            print(id)
            topic_arr.append(id)

    return topic_arr


def convert_ids_categories(ids, categories):
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


def convert_embedded_URL(embeddedTag):
    elements = embeddedTag.split(" ")
    url = ""
    for el in elements:
        if el.startswith("src="):
            el = el.replace("src=", "")
            url = el.replace('"', "")
            break
    return url.replace('http', 'https')


def convert_keywords(keywords):
    keyword_arr = []
    words = keywords.split(" ")
    for i in range(len(words)):
        if words[i].startswith('"'):
            phrase = ""
            while not words[i].endswith('"'):
                phrase = phrase + words[i].replace('"', "") + " "
                i += 1
            phrase = phrase + words[i].replace('"', "")
            keyword_arr.append(phrase)
        else:
            keyword_arr.append(words[i])

    return keyword_arr