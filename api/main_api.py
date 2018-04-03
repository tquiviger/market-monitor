import json

import requests


def call_get(url):
    try:
        api_response = requests.get(url=url, headers={"Content-Type": "application/json"}, timeout=10)
    except requests.Timeout:
        print("Timeout")
        return json.loads('{"data":[],"meta":{}}')
    if api_response.ok:

        # Loading the response data into a dict variable
        # json.loads takes in only binary or string variables so using content to fetch binary content
        return json.loads(api_response.content)
    else:
        # If response code is not ok (200), print the resulting http error code with description
        api_response.raise_for_status()
