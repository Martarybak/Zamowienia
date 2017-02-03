# -*- coding: utf-8 -*-

import sqlite3


db_path = 'zamowienia.db'
conn = sqlite3.connect(db_path)

c = conn.cursor()
#
# Tabele
#
c.execute('''
          CREATE TABLE Zamowienia
          ( id INTEGER PRIMARY KEY,
            data DATE NOT NULL,
            ilosc NUMERIC NOT NULL
          )
          ''')
c.execute('''
          CREATE TABLE Produkty
          ( nazwa VARCHAR(20),
            ilosc NUMERIC NOT NULL,
            cena INTEGER NOT NULL,
            zamowienia_id INTEGER,
           FOREIGN KEY(Zamowienia_id) REFERENCES Zamowienia(id),
           PRIMARY KEY (nazwa, zamowienia_id))
          ''')
