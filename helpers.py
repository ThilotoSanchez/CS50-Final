import requests
import json
import sqlite3
import os
from icecream import ic
from requests.exceptions import HTTPError
from flask import redirect, render_template, request, session
from dotenv import load_dotenv
from datetime import datetime
from functools import wraps
from urllib.request import urlopen
import pytz
import itertools

# ! Delrecated method, do not use
# ? Questions?
# TODO: write to-do here

load_dotenv()

# get SQLITE3 ready
conn = sqlite3.connect('cov19db.sqlite')
db = conn.cursor()

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def getCountries():
    url = "https://covid-193.p.rapidapi.com/statistics"

    # optional country parameter
    # querystring = {"country": country}

    headers = {
        'x-rapidapi-key': os.getenv('x-rapidapi-key'),
        'x-rapidapi-host': os.getenv('x-rapidapi-host')
        }

    try:
        response = requests.request("GET", url, headers=headers)
        response.raise_for_status()

        # use builtin JSON decoder
        jsonResponse = response.json()

        #ic(jsonResponse['response'])

        for i in jsonResponse['response']:
            #ic(i)
            country = i['country']
            continent = i['continent']
            population = i['population']

            if population != None:
                # fill database
                conn = sqlite3.connect('cov19db.sqlite')
                db = conn.cursor()
                db.execute('''INSERT OR IGNORE INTO countries
                    ( name, continent, population ) VALUES ( ?, ?, ? )''', 
                    ( country, continent, population, ))
                conn.commit() 
    
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

def getStatistics(country):
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

def getHistory(country):
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
    db.execute("""SELECT id FROM countries WHERE name == ?""", (country, ))
    country_id = db.fetchall()
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

            # transform day into datetime
            time_str = item['time']
            daytime = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S+%f:00')

            # get list specific fields
            # fill cases db
            if i == 'cases':
                new = item[i]['new']
                ic(new)
                active = item[i]['active']
                ic(active)
                critical = item[i]['critical']
                ic(critical)
                recovered = item[i]['recovered']
                ic(recovered)

                db.execute('''INSERT OR IGNORE INTO cases
                ( total, '1M_POP', daytime, country_id, new, active, critical, recovered ) VALUES ( ?, ?, ?, ?, ?, ?, ?, ? )''',
                ( total, POP_1M, daytime, country_id, new, active, critical, recovered, ))
                conn.commit()

            # fill deaths db
            elif i == 'deaths':
                new = item[i]['new']

                db.execute('''INSERT OR IGNORE INTO deaths
                ( total, '1M_POP', daytime, country_id, new ) VALUES ( ?, ?, ?, ?, ? )''',
                ( total, POP_1M, daytime, country_id, new, ))
                conn.commit()

            # fill tests db
            elif i == 'tests':
                db.execute('''INSERT OR IGNORE INTO tests
                ( total, '1M_POP', daytime, country_id ) VALUES ( ?, ?, ?, ? )''',
                ( total, POP_1M, daytime, country_id, ))
                conn.commit()

def countriesDB():
        # get SQLITE3 ready
        conn = sqlite3.connect('cov19db.sqlite')
        db = conn.cursor()
        
        # get current list of countries from db
        db.execute('SELECT name FROM countries')
        countries = db.fetchall()
        conn.commit()
        countries = list(itertools.chain(*countries))
        return countries

getCountries()
# getStatistics("Germany")
# getHistory("Germany")