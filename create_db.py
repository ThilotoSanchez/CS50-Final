import sqlite3

def create_new_db():
    conn = sqlite3.connect('cov19db.sqlite')
    cur = conn.cursor()

    # set up tables
    
    cur.executescript('''
    CREATE TABLE countries (
        id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        name      TEXT UNIQUE,
        continent     TEXT,
        population     INTEGER
    );

    CREATE TABLE IF NOT EXISTS cases (
        id    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        country_id     INTEGER,
        total     INTEGER,
        new     TEXT,
        active     INTEGER,
        critical     INTEGER,
        recovered     INTEGER,
        '1M_POP'     TEXT,
        day     TEXT,
        time     TEXT
    );

    CREATE TABLE IF NOT EXISTS tests (
        id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        country_id     INTEGER,
        total     INTEGER,
        '1M_POP'     TEXT,
        day     TEXT,
        time     TEXT
    );

    CREATE TABLE IF NOT EXISTS deaths (
        id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        country_id     INTEGER,
        total     INTEGER,
        new     TEXT,
        '1M_POP'     TEXT,
        day     TEXT,
        time     TIME
    );

    CREATE TABLE IF NOT EXISTS user (
        id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        username     TEXT UNIQUE,
        pw_hash     TEXT
    )
    ''')

    conn.commit()

create_new_db()