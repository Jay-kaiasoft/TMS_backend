import pymysql
import pymysql.cursors
from typing import Generator

# Database configuration (should use env vars in production)
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "" # Please change according to your local DB
DB_NAME = "tms"

def get_db_connection():
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

def get_db() -> Generator:
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()
