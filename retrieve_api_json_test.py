import requests
import pprint as pp

params = {
    'access_key': '3f69b854db358b9beae52bf6beb5d79f',
    'type': 'shopping',
    'query': 'Fitness'
}

api_result = requests.get("http://api.serpstack.com/search", params)
api_result_in_json = api_result.json()

pp.pprint(api_result_in_json)
