from datetime import datetime
import sqlite3

# get SQLITE3 ready
conn = sqlite3.connect('cov19db.sqlite')
cur = conn.cursor()

time_str = "2021-05-03T22:45:02+00:00"

date_time_obj = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S+%f:00')

cur.execute('''INSERT OR IGNORE INTO cases
                ( daytime ) VALUES ( ? )''',
                ( date_time_obj, ))
conn.commit()