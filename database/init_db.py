import sqlite3

import sqlite3
from datetime import datetime


connection = sqlite3.connect('projects.db')
with open('projects_schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()
connection.commit()
connection.close()