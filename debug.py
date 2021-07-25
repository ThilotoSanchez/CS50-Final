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

# get SQLITE3 ready
conn = sqlite3.connect('cov19db.sqlite')
db = conn.cursor()

COUNTRIES = checkCountries()

current_stats = list()

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
    
    try:
        country_specs = list(country_specs)
    except:
        pass
    
    conn.commit()

    ic(country_specs)

    # ic(country_specs)
    current_stats.append(country_specs)

ic(current_stats)