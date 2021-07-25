import requests
import json
import sqlite3
import os
import pandas as pd
from icecream import ic
from requests.exceptions import HTTPError
from flask import redirect, render_template, request, session
from dotenv import load_dotenv
from datetime import datetime, date
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
    """ Calls the COVID-19 statistics API. It delivers a list of all countries that are supported. """
    
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
    """ Calls the COVID-19 statistics API. It delivers todays stats for a specific country """
    
    countries = checkCountries()
    if country not in countries:
        return 404

    # get SQLITE3 ready
    conn = sqlite3.connect('cov19db.sqlite')
    db = conn.cursor()

    # get country_id
    db.execute("""SELECT id FROM countries WHERE name == ?""", (country, ))
    country_id = db.fetchall()
    conn.commit()
    country_id = country_id[0][0]

    url = "https://covid-193.p.rapidapi.com/statistics"

    # optional country parameter
    querystring = {"country": country}

    headers = {
        'x-rapidapi-key': os.getenv('x-rapidapi-key'),
        'x-rapidapi-host': os.getenv('x-rapidapi-host')
        }

    try:
        response = requests.request("GET", url, headers=headers, params=querystring)

        # use builtin JSON decoder
        jsonResponse = response.json()

        for item in jsonResponse['response']:
            active_cases = item['cases']['active']
            deaths = item['deaths']['total']
            tests = item['tests']['total']
            updated = item['day']
    
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

    # get SQLITE3 ready
    conn = sqlite3.connect('cov19db.sqlite')
    db = conn.cursor()

    # update db
    db.execute('''INSERT OR IGNORE INTO overview
        ( country_id, new, active, critical, recovered, day ) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ? )''',
        ( total, POP_1M, daytime, country_id, new, active, critical, recovered, day, ))
    conn.commit()

def getHistory(country):
    
    # check if country input is valid
    countries = checkCountries()
    if country not in countries:
        return 404

    # make API request
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

    # get SQLITE3 ready
    conn = sqlite3.connect('cov19db.sqlite')
    db = conn.cursor()
    
    # get country_id
    db.execute("""SELECT id FROM countries WHERE name == ?""", (country, ))
    country_id = db.fetchall()
    conn.commit()
    country_id = country_id[0][0]

    lists = ['cases', 'tests', 'deaths']
            
    # iterate through JSON from API
    for item in jsonResponse['response']:
        # ic(item)

        try:
            # select data for all three cases
            for i in lists:
                total = item[i]['total']
                POP_1M = item[i]['1M_pop']

                day = item['day']

                # transform day and time into datetime
                time_str = item['time']
                daytime = time_str.split('T')[1].split('+')[0]

                # get list specific fields
                # fill cases db
                if i == 'cases':
                    
                    new = item[i]['new']
                    active = item[i]['active']
                    critical = item[i]['critical']
                    recovered = item[i]['recovered']

                    # check if date exists in database
                    db.execute('''SELECT day, daytime FROM cases WHERE day = ? AND country_id = ?''', (day, country_id, ) )
                    date = db.fetchall()
                    conn.commit()

                    # if day already exists but time is greater: replace row
                    if len(date) > 0:
                        
                        tempDay = date[0][0]
                        tempDaytime = date[0][1]

                        # update data if timestamp is greater
                        if day == tempDay and daytime > tempDaytime:
                            db.execute('''UPDATE cases SET 
                                total = ?,
                                '1M_POP' = ?,
                                daytime = ?,
                                new = ?,
                                active = ?,
                                critical = ?,
                                recovered = ?,
                                day = ?, 
                                WHERE country_id = ?''', 
                                ( total, POP_1M, daytime, new, active, critical, recovered, day, country_id, ))
                            conn.commit()

                    # data for day doesn't exist, create it
                    else:
                        db.execute('''INSERT OR IGNORE INTO cases
                            ( total, '1M_POP', daytime, country_id, new, active, critical, recovered, day ) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ? )''',
                            ( total, POP_1M, daytime, country_id, new, active, critical, recovered, day, ))
                        conn.commit()

                # fill deaths db
                elif i == 'deaths':
                    new = item[i]['new']

                    # check if date exists in database
                    db.execute('''SELECT day, daytime FROM deaths WHERE day = ? AND country_id = ?''', (day, country_id, ) )
                    date = db.fetchall()
                    conn.commit()

                    
                    # if day already exists but time is greater: replace row
                    if len(date) > 0:
                        
                        tempDay = date[0][0]
                        tempDaytime = date[0][1]

                        # update data if timestamp is greater
                        if day == tempDay and daytime > tempDaytime:
                            db.execute('''UPDATE deaths SET 
                                total = ?,
                                '1M_POP' = ?,
                                daytime = ?,
                                new = ?,
                                day = ?, 
                                WHERE country_id = ?''',
                                ( total, POP_1M, daytime, new, day, country_id, ))
                            conn.commit()

                    # data for day doesn't exist, create it
                    else:
                        db.execute('''INSERT OR IGNORE INTO deaths
                            ( total, '1M_POP', daytime, country_id, new, day ) VALUES ( ?, ?, ?, ?, ?, ? )''',
                            ( total, POP_1M, daytime, country_id, new, day, ))
                        conn.commit()

                # fill tests db
                elif i == 'tests':

                    # check if date exists in database
                    db.execute('''SELECT day, daytime FROM tests WHERE day = ? AND country_id = ?''', (day, country_id, ) )
                    date = db.fetchall()
                    conn.commit()

                    # if day already exists but time is greater: replace row
                    if len(date) > 0:
                        
                        tempDay = date[0][0]
                        tempDaytime = date[0][1]

                        # update data if timestamp is greater
                        if day == tempDay and daytime > tempDaytime:
                            db.execute('''UPDATE tests SET 
                                total = ?,
                                '1M_POP' = ?,
                                daytime = ?,
                                day = ?, 
                                WHERE country_id = ?''',
                                ( total, POP_1M, daytime, day, country_id, ))
                            conn.commit()

                    # data for day doesn't exist, create it
                    else:
                        db.execute('''INSERT OR IGNORE INTO tests
                            ( total, '1M_POP', daytime, country_id, day ) VALUES ( ?, ?, ?, ?, ? )''',
                            ( total, POP_1M, daytime, country_id, day, ))
                        conn.commit()

        except:
            continue

def checkCountries():
        # get SQLITE3 ready
        conn = sqlite3.connect('cov19db.sqlite')
        db = conn.cursor()
        
        # get current list of countries from db
        db.execute('SELECT name FROM countries')
        countries = db.fetchall()
        conn.commit()
        countries = list(itertools.chain(*countries))
        
        # ic(countries)
        return countries

def checkHistory(country):
    ''' Checks database to see when the data was updated for the last time '''

    # connect to db and get last updated data
    conn = sqlite3.connect('cov19db.sqlite')
    db = conn.cursor()
    
    db.execute("""
    SELECT cases.day AS day
    FROM cases
    JOIN countries ON cases.country_id = countries.id
    WHERE countries.name == ?
    ORDER BY day DESC
    LIMIT 1""", (country,) )
    
    last_updated = db.fetchone()[0]
    # ic(last_updated)

    conn.commit()
    
    return last_updated

def chartJS(COUNTRY):
    """ Builds beautiful charts using Chart.JS
    Documentation: https://www.chartjs.org/
    """
    
    # get data from SQLITE3 db
    conn = sqlite3.connect('cov19db.sqlite')
    db = conn.cursor()
    db.execute("""SELECT cases.day AS Time, cases.total AS Cases, deaths.total AS Deaths
        FROM cases
        JOIN countries ON cases.country_id = countries.id
        JOIN deaths ON (cases.country_id = deaths.country_id AND cases.day = deaths.day)
        WHERE countries.name == ?
        ORDER BY Time DESC
        LIMIT 600""", (COUNTRY, ))

    data = db.fetchall()
    conn.commit()

    # reduce labels to once per month
    labels = list()
    for i in range(0, len(data), 29):
        labels.append(data[i][0])
    labels.reverse()
    
    # get cases values
    valuesCases = list()
    for i in range(0, len(data), 29):
        valuesCases.append(data[i][1])
    valuesCases.reverse()

    # get deaths values
    valuesDeaths = list()
    for i in range(0, len(data), 29):
        valuesDeaths.append(data[i][2])
    valuesDeaths.reverse()

    return labels, valuesCases, valuesDeaths

def todaysNrs(country, today):
    ''' Get todays numbers out of the database '''

    # get SQLITE3 ready
    conn = sqlite3.connect('cov19db.sqlite')
    db = conn.cursor()
    
    # get country_id
    db.execute("""SELECT cases.total, deaths.total, tests.total, cases.active, cases.critical, cases.recovered , countries.population, cases.new, cases.day
    FROM cases
    JOIN countries ON cases.country_id = countries.id
    JOIN deaths ON (cases.country_id = deaths.country_id AND cases.day = deaths.day)
    JOIn tests ON (cases.country_id = tests.country_id AND cases.day = tests.day)
    WHERE countries.name == ? AND cases.day = ?""", (country, today))
    todays_numbers = db.fetchone()
    todays_numbers = list(todays_numbers)
    conn.commit()

    for i in range(0, 7):
        try:
            todays_numbers[i] = f'{todays_numbers[i]:,}'
        except:
            continue

    # ic(type(todays_numbers))
    # ic(todays_numbers)

    return todays_numbers

# getCountries()
# getStatistics("Germany")
# getHistory("USA")
# checkHistory("Germany")
# chartJS("Germany")
# checkCountries()
# todaysNrs("Germany", "2021-07-24")