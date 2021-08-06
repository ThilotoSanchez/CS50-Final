from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from icecream import ic
import json
from urllib.request import urlopen
import pytz
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, date
import itertools
import sqlite3

from helpers import apology, getHistory, checkCountries, checkHistory, chartJS, todaysNrs

# configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

if __name__ == '__main__':
    app.run(debug=True)

today = str(date.today())

@app.route('/', methods=["GET", "POST"])
def index():

    if request.method == "GET":
        # TODO: check db if last values are from today
        # if values from today: use those values
        # else: make API request to update db

        # load countries from db
        COUNTRIES = checkCountries()

        # check if user already has cookie
        if session.get('country'):
            COUNTRY = session.get('country')
            print("User had country cookie:", COUNTRY)
        else:
            # get user location
            # pytz transfers country ISO code into country name
            url = 'http://ipinfo.io/json'
            response = urlopen(url)
            location = json.load(response)
            COUNTRY = location['country']
            COUNTRY = pytz.country_names[COUNTRY]
            print("User didn't have country cookie. We set up:", COUNTRY)

            if COUNTRY not in COUNTRIES:
                COUNTRY = "Switzerland"
                print("Country wasn't supported. We set it to Switzerland.")

            # set cookie in order to customize frontend
            session['country'] = COUNTRY

        # check when data was last time updated
        try:
            last_updated = checkHistory(COUNTRY)
            ic(last_updated)
        except:
            getHistory(COUNTRY)
            last_updated = checkHistory(COUNTRY)

        if last_updated != today:
            getHistory(COUNTRY)
        
        # get todays numbers to display in frontend
        # order: cases, deaths, tests
        todays_numbers = todaysNrs(COUNTRY, today, last_updated)

        # create chart using chartJS
        labels, valuesCases, valuesDeaths = chartJS(COUNTRY)

        return render_template("index.html", country=COUNTRY, countries=COUNTRIES, labels=labels, 
            valuesCases=valuesCases, valuesDeaths=valuesDeaths, todays_numbers=todays_numbers)

    # user coming via POST
    else:
        
        # load countries from db
        COUNTRIES = checkCountries()

        COUNTRY = request.form.get("countries")

        if COUNTRY not in COUNTRIES:
            return apology("country has no data yet", 404)
        
        session['country'] = COUNTRY

        # Redirect user to home page
        return redirect("/")

@app.route("/statistics")
def statistics():

    if request.method == "GET":

        # get SQLITE3 ready
        conn = sqlite3.connect('cov19db.sqlite')
        db = conn.cursor()
        
        COUNTRIES = checkCountries()

        STATISTICS = list()

        for country in COUNTRIES:

            # query database to show data for all countries
            db.execute("""SELECT countries.name, cases.active, deaths.total, tests.total, cases.day
                FROM cases
                JOIN countries ON cases.country_id = countries.id
                JOIN deaths ON (cases.country_id = deaths.country_id AND cases.day = deaths.day)
                JOIN tests ON (cases.country_id = tests.country_id AND cases.day = tests.day)
                WHERE countries.name = ?
                ORDER BY cases.day DESC
                LIMIT 1""", (country,))
            country_specs = db.fetchone()
            conn.commit()

            # format active cases, deaths and tests
            try:
                country_specs = list(country_specs)
                country_specs[1] = f'{country_specs[1]:,}'
            except:
                pass

            try:
                country_specs = list(country_specs)
                country_specs[2] = f'{country_specs[2]:,}'
            except:
                pass

            try:
                country_specs = list(country_specs)
                country_specs[3] = f'{country_specs[3]:,}'
            except:
                pass

            # try to format 


            # ic(country_specs)
            STATISTICS.append(country_specs)

        return render_template("statistics.html", statistics=STATISTICS)


@app.route("/legal-notice")
def legalnotice():

    if request.method == "GET":
        pass
    return render_template("imprint.html")

@app.route("/data-privacy")
def dataprivacy():

    if request.method == "GET":
        pass
    return render_template("data-privacy.html")