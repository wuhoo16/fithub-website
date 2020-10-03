import requests
import pprint as pp

# Note that by using the SerpStack free plan, you are limited to 98 more API requests for the month of October.

params = {
    'access_key': '3ebc6a73b26d9b40ba9f4805ea002955',
    'type': 'shopping',
    'query': 'Weightlifting Belt'
}

api_result = requests.get("http://api.serpstack.com/search", params)
api_result_in_json = api_result.json()

pp.pprint(api_result_in_json)