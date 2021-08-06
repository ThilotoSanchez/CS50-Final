import requests
import json
import sqlite3
import os
from icecream import ic
from requests.exceptions import HTTPError
from flask import redirect, render_template, request, session
from dotenv import load_dotenv
from datetime import datetime, date
from functools import wraps
from urllib.request import urlopen
import pytz
import pandas as pd
import itertools

from helpers import checkCountries

def getStatistics(country):
    """ Calls the COVID-19 statistics API. It delivers todays stats for a specific country """
    
    countries = checkCountries()
    if country not in countries:
        return 404

    # get SQLITE3 ready
    # get country_id
    conn = sqlite3.connect('cov19db.sqlite')
    db = conn.cursor()
    
    db.execute("""SELECT id FROM countries WHERE name == ?""", (country, ))
    country_id = db.fetchall()
    conn.commit()
    country_id = country_id[0][0]

    url = "https://covid-193.p.rapidapi.com/statistics"

    # optional country parameter
    querystring = {"country": country}

    headers = {
        'x-rapidapi-key': os.environ.get('x-rapidapi-key'),
        'x-rapidapi-host': os.environ.get('x-rapidapi-host')
        }

    try:
        response = requests.request("GET", url, headers=headers, params=querystring)

        # use builtin JSON decoder
        jsonResponse = response.json()

        for item in jsonResponse['response']:
            cases_active = item['cases']['active']
            cases_total = item['cases']['total']
            cases_critical = item['cases']['critical']
            cases_1mpop = item['cases']['1M_pop']
            cases_recovered = item['cases']['recovered']
            cases_new = item['cases']['new']
            deaths_total = item['deaths']['total']
            deaths_new = item['deaths']['total']
            deaths_1mpop = item['deaths']['1M_pop']
            tests_total = item['tests']['total']
            tests_1mpop = item['tests']['1M_pop']
            updated = item['day']

            # transform day and time into datetime
            time_str = item['time']
            daytime = time_str.split('T')[1].split('+')[0]
            
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

    # get SQLITE3 ready
    conn = sqlite3.connect('cov19db.sqlite')
    db = conn.cursor()

    # update cases db
    db.execute('''INSERT OR IGNORE INTO cases
        ( country_id, total, new, active, critical, recovered, '1M_POP', daytime, day ) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ? )''',
        ( country_id, cases_total, cases_new, cases_active, cases_critical, cases_recovered, cases_1mpop, daytime, updated, ))
    conn.commit()

    # update deaths db
    db.execute('''INSERT OR IGNORE INTO deaths
        ( country_id, total, new, '1M_POP', daytime, day ) VALUES ( ?, ?, ?, ?, ?, ? )''',
        ( country_id, deaths_total, deaths_new, deaths_1mpop, daytime, updated, ))
    conn.commit()

    # update tests db
    db.execute('''INSERT OR IGNORE INTO tests
        ( country_id, total, '1M_POP', daytime, day ) VALUES ( ?, ?, ?, ?, ?, ? )''',
        ( country_id, tests_total, tests_1mpop, daytime, updated, ))
    conn.commit()

getStatistics("Switzerland")