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

load_dotenv()



statistics("Germany")