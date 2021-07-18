import requests
import json
import os
from requests.exceptions import HTTPError

def getCountries():
    url = "https://covid-193.p.rapidapi.com/countries"

    headers = {
        'x-rapidapi-key': x-rapidapi-key,
        'x-rapidapi-host': x-rapidapi-host
        }

    try:
        response = requests.request("GET", url, headers=headers)
        response.raise_for_status()

        # use builtin JSON decoder
        jsonResponse = response.json()
        
        # access JSON content
        
        #print(jsonResponse)
        for country in jsonResponse['response']:
        print(country)

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')