from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from icecream import ic
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import sqlite3

from helpers import login_required, apology, getCountries, statistics, history

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

# get SQLITE3 ready
conn = sqlite3.connect('cov19db.sqlite')
db = conn.cursor()

@app.route('/', methods=["GET"])
@login_required
def index():

    if request.method == "GET":
        # TODO: check db if last values are from today
        # if values from today: use those values
        # else: make API request to update db

        return render_template("index.html")
        # return render_template("index.html", )

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
       
        # Ensure username was submitted
        if len(request.form.get("username")) < 3:
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif len(request.form.get("password")) < 3:
            return apology("must provide password", 400)

        # Ensure password confirmation was submitted
        elif len(request.form.get("confirmation")) < 3:
            return apology("must provide password confirmation", 400)

        # Ensure password and confirmation are equal
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("password and confirmation must be equal", 400)

        # Ensure username doesn't exists
        conn = sqlite3.connect('cov19db.sqlite')
        db = conn.cursor()
        db.execute("SELECT * FROM user WHERE username = ?", (request.form.get("username"),) )
        rows = db.fetchall()
        conn.commit()

        if len(rows) >= 1:
            return apology("user already exists", 400)

        # Query database for username
        db.execute("INSERT INTO user (username, pw_hash) VALUES (?, ?)", (request.form.get("username"), generate_password_hash(request.form.get("password"), )) )
        conn.commit()

        # Redirect user to home page
        return redirect("/login")

        # TODO: implement success message for user

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # set up database connection
        conn = sqlite3.connect('cov19db.sqlite')
        db = conn.cursor()

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for id, username, pw_hash values
        db.execute("SELECT * FROM user WHERE username = ?", (request.form.get("username"),))
        rows = list(db.fetchall())
        conn.commit()

        ic(type(rows))
        ic(rows)
        ic(len(rows))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/password_reset", methods=["GET", "POST"])
def password_reset():

    # set up database connection
    conn = sqlite3.connect('cov19db.sqlite')
    db = conn.cursor()

    """Let user reset password"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username doesn't exists
        rows = db.execute("SELECT * FROM user WHERE username = ?", request.form.get("username"))
        if len(rows) != 1:
            return apology("username correct?", 400)

        # add new password into database for username
        db.execute("UPDATE user SET pw_hash = ? WHERE username = ?", generate_password_hash(request.form.get("npassword")), request.form.get("username"))

        conn.commit()
        return redirect("/login")

    else:
        return render_template("password_reset.html")