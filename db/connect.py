import mariadb
import sys

def connectDB():
    try:
        conn = mariadb.connect(
            user="root",
            password="life4died1",
            host="127.0.0.1",
            port=3307,
            database='stocks'
        )
    except mariadb.Error as e:
        raise RuntimeError(f"Error connecting to MariaDB: {e}")

    return conn, conn.cursor()               