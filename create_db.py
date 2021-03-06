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
        daytime     TEXT,
        day     TEXT,
        UNIQUE(country_id, daytime)
    );

    CREATE TABLE IF NOT EXISTS tests (
        id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        country_id     INTEGER,
        total     INTEGER,
        '1M_POP'     TEXT,
        daytime     TEXT,
        day     TEXT,
        UNIQUE(country_id, daytime)
    );

    CREATE TABLE IF NOT EXISTS deaths (
        id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        country_id     INTEGER,
        total     INTEGER,
        new     TEXT,
        '1M_POP'     TEXT,
        daytime     TEXT,
        day     TEXT,
        UNIQUE(country_id, daytime)
    );

    CREATE TABLE IF NOT EXISTS overview (
        id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        country_id     INTEGER,
        active_cases     INTEGER,
        deaths     INTEGER,
        tests     INTEGER,
        updated     TEXT,
        UNIQUE(country_id, updated)
    )

    CREATE TABLE IF NOT EXISTS user (
        id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        username     TEXT UNIQUE,
        pw_hash     TEXT,
        created     DATE
    )
    ''')

    conn.commit()

create_new_db()