import requests
import json
import os
from requests.exceptions import HTTPError
from dotenv import load_dotenv

# ! Delrecated method, do not use
# ? Questions?
# TODO: write to-do here

load_dotenv()

def getCountries():
    url = "https://covid-193.p.rapidapi.com/countries"

    headers = {
        'x-rapidapi-key': os.getenv('x-rapidapi-key'),
        'x-rapidapi-host': os.getenv('x-rapidapi-host')
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

def statistics():
    url = "https://covid-193.p.rapidapi.com/statistics"

    # optional country parameter
    querystring = {"country":"Germany"}

    headers = {
        'x-rapidapi-key': os.getenv('x-rapidapi-key'),
        'x-rapidapi-host': os.getenv('x-rapidapi-host')
        }

    try:
        response = requests.request("GET", url, headers=headers, params=querystring)

        print(response.text)
    
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

statistics()