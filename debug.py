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

COUNTRIES = checkCountries()
ic(COUNTRIES)