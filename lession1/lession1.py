import requests
import json
from pprint import pprint

user_id = '22758623'
access_token = '***'
response = 'https://api.vk.com/method/groups.get'
version = '5.131'
params = {'user_id': user_id,
          'count': 5,
          'extended': 1,
          'access_token': access_token,
          'v': version
   }
req = requests.get(response, params=params)
json_data = req.json()
pprint(json_data)

with open('data.json', 'w') as w_obj:
    json.dump(json_data, w_obj, ensure_ascii=False, indent=4)
