import mariadb
import sys
from dotenv import load_dotenv
import os

def connectDB():
    load_dotenv
    try:
        conn = mariadb.connect(
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_DATABASE')
        )
    except mariadb.Error as e:
        raise RuntimeError(f"Error connecting to MariaDB: {e}")

    return conn, conn.cursor()               