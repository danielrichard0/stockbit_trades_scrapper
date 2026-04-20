import csv
import mariadb, sys
from datetime import datetime, date

BULAN = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
    "Mei": 5, "Jun": 6, "Jul": 7, "Agt": 8,
    "Sep": 9, "Okt": 10, "Nov": 11, "Des": 12
}

def parse_tanggal(s):
    day, month, year = s.split()
    return date(int(year), BULAN[month], int(day))

parse = []
with open('daftar_saham_bei_18_03_2026.csv', mode='r', newline='') as file:
    reader = csv.reader(file)
    for row in reader:
        row.pop(0) 
        row[2] = parse_tanggal(row[2])
        parse.append(row)        
      
try:
    conn = mariadb.connect(
        user="root",
        password="life4died1",
        host="127.0.0.1",
        port=3307,
        database="stocks"
    )        
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

cur = conn.cursor()
cur.executemany("INSERT INTO stock_symbols (stock_symbol, stock_name, register_date) VALUES (?, ?, ?)", parse) 
conn.commit()
cur.close()
conn.close()