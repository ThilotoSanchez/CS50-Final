import requests
import json
import sqlite3
import os
from icecream import ic
from requests.exceptions import HTTPError
from dotenv import load_dotenv

# ! Delrecated method, do not use
# ? Questions?
# TODO: write to-do here

load_dotenv()

# get SQLITE3 ready
conn = sqlite3.connect('cov19db.sqlite')
cur = conn.cursor()

def getCountries(country):
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
                
        #print(jsonResponse)
        for country in jsonResponse['response']:
            ic(country)
            cur.execute('''INSERT OR IGNORE INTO countries
                ( name ) VALUES ( ? )''',
                ( country, ))
            conn.commit()

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

def statistics():
    url = "https://covid-193.p.rapidapi.com/statistics"

    # optional country parameter
    querystring = {"country": country}

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

def history(country):
    url = "https://covid-193.p.rapidapi.com/history"

    querystring = {"country": country}

    headers = {
        'x-rapidapi-key': os.getenv('x-rapidapi-key'),
        'x-rapidapi-host': os.getenv('x-rapidapi-host')
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    response.raise_for_status()

    # use builtin JSON decoder
    jsonResponse = response.json()

    # get country_id
    cur.execute("""SELECT id FROM countries WHERE name == ?""", (country, ))
    country_id = cur.fetchall()
    conn.commit()
    country_id = country_id[0][0]

    lists = ['cases', 'tests', 'deaths']
            
    # iterate through JSON from API
    for item in jsonResponse['response']:
        
        # select data for all three cases
        for i in lists:
            total = item[i]['total']
            ic(total)
            POP_1M = item[i]['1M_pop']
            ic(POP_1M)

            # TODO: transform day into datetime; change db field to DATE
            day = item['day']
            ic(day)
            time = item['time']
            ic(time)

            # get list specific fields
            # write values in database
            if i == 'cases':
                new = item[i]['new']
                ic(new)
                active = item[i]['active']
                ic(active)
                critical = item[i]['critical']
                ic(critical)
                recovered = item[i]['recovered']
                ic(recovered)

                cur.execute('''INSERT OR IGNORE INTO cases
                ( total, '1M_POP', day, time, country_id, new, active, critical, recovered ) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ? )''',
                ( total, POP_1M, day, time, country_id, new, active, critical, recovered, ))
                conn.commit()

            elif i == 'deaths':
                new = item[i]['new']

                cur.execute('''INSERT OR IGNORE INTO deaths
                ( total, '1M_POP', day, time, country_id, new ) VALUES ( ?, ?, ?, ?, ?, ? )''',
                ( total, POP_1M, day, time, country_id, new, ))
                conn.commit()

            elif i == 'tests':
                cur.execute('''INSERT OR IGNORE INTO tests
                ( total, '1M_POP', day, time, country_id ) VALUES ( ?, ?, ?, ?, ? )''',
                ( total, POP_1M, day, time, country_id, ))
                conn.commit()

# getCountries("Germany")
# statistics("Germany")
history("Germany")