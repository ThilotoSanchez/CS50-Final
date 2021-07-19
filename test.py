import sqlite3

def create_new_db():
    conn = sqlite3.connect('spendings.sqlite')
    cur = conn.cursor()

    # set up table
    cur.executescript('''
    CREATE TABLE IF NOT EXISTS spendings (
        id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        account   TEXT,
        'date'   DATE,
        amount   FLOAT,
        currency   TEXT,
        purpose   TEXT,
        cat_id   INTEGER,
        subcat_id   INTEGER,
        SEPA    TEXT,
        db_added    DATE,
        UNIQUE ('date', amount, purpose, SEPA, db_added)
    );

    CREATE TABLE IF NOT EXISTS category (
        id    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        cat  TEXT UNIQUE
    )
    ''')
    conn.commit()

create_new_db()
