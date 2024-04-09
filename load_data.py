import pandas as pd
import sqlite3
from datetime import datetime
from ApiMaps import search_store_by_name

data_revolut = pd.read_csv("data/revolut/account-statement_2022-07-01_2024-04-06.csv")
data_popso = pd.read_csv("data/popso/movimentiCartaTotale.csv")


data_revolut.pop("Type")
data_revolut.pop("Product")
data_revolut.pop("Completed Date")
data_revolut.pop("Fee")
data_revolut.pop("Currency")
data_revolut.pop("State")


conn = sqlite3.connect('budget_tracker.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    account TEXT,
                    category TEXT,
                    description TEXT,
                    amount REAL

                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT,
                    last_name TEXT,
                    email TEXT,
                    username TEXT, 
                    password TEXT,
                    role TEXT

                )''')

for i in range(len(data_revolut)):
    date = datetime.strptime(data_revolut.iloc[i]["Started Date"], "%Y-%m-%d %H:%M:%S").strftime("%Y/%m/%d")
    description = data_revolut.iloc[i]["Description"].strip()
    amount = data_revolut.iloc[i]["Amount"]
    cursor.execute('''INSERT INTO transactions (account, date, category, description, amount)
                      VALUES (?, ?, ?, ?, ?)''', ("Revolut", date, search_store_by_name(description),  description, amount))




for i in range(len(data_popso)):
    date = datetime.strptime(data_popso.iloc[i]["Data"], "%d/%m/%Y %H.%M.%S").strftime("%Y/%m/%d")
    description = data_popso.iloc[i]["Causale"].strip()
    amount = data_popso.iloc[i]["Segno"] + data_popso.iloc[i]["Importo"].replace(".", "").replace(",", ".")
    cursor.execute('''INSERT INTO transactions (account, date, category, description, amount)
                      VALUES (?, ?, ?, ?, ?)''', ("Popso", date, search_store_by_name(description), description, amount))


conn.commit()
conn.close()



