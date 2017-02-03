# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime

#
# Ścieżka połączenia z bazą danych
#
db_path = 'zamowienia.db'

#
# Wyjątek używany w repozytorium
#
class RepositoryException(Exception):
    def __init__(self, message, *errors):
        Exception.__init__(self, message)
        self.errors = errors


#
# Model danych
#
class Zamowienia():

    def __init__(self, id, data=datetime.now(), produkty=[]):
        self.id = id
        self.data = data
        self.produkty = produkty
        self.ilosc = sum([prod.ilosc*prod.cena for prod in self.produkty])

    def __repr__(self):
        return "<Zamowienia(id='%s', data='%s', ilosc='%s', prods='%s')>" % (
                    self.id, self.data, str(self.ilosc), str(self.produkty)
                )


class Produkt():


    def __init__(self, nazwa, ilosc, cena):
        self.nazwa = nazwa
        self.ilosc = ilosc
        self.cena = cena

    def __repr__(self):
        return "<Produkt(nazwa='%s', ilosc='%s', cena='%s')>" % (
                    self.nazwa, str(self.ilosc), str(self.cena)
                )


#
# Klasa bazowa repozytorium
#
class Repository():
    def __init__(self):
        try:
            self.conn = self.get_connection()
        except Exception as e:
            raise RepositoryException('GET CONNECTION:', *e.args)
        self._complete = False

    # wejście do with ... as ...
    def __enter__(self):
        return self

    # wyjście z with ... as ...
    def __exit__(self, type_, value, traceback):
        self.close()

    def complete(self):
        self._complete = True

    def get_connection(self):
        return sqlite3.connect(db_path)

    def close(self):
        if self.conn:
            try:
                if self._complete:
                    self.conn.commit()
                else:
                    self.conn.rollback()
            except Exception as e:
                raise RepositoryException(*e.args)
            finally:
                try:
                    self.conn.close()
                except Exception as e:
                    raise RepositoryException(*e.args)

#
# repozytorium obiektow
#
class ZamowieniaRepository(Repository):

    def add(self, zamowienia):

        try:
            c = self.conn.cursor()
            # zapisz nagłowek faktury
            ilosc = sum([prod.ilosc*prod.cena for prod in zamowienia.produkty])
            c.execute('INSERT INTO Zamowienia (id, data, ilosc) VALUES(?, ?, ?)',
                        (zamowienia.id, str(zamowienia.data), zamowienia.ilosc)
                    )
            # zapisz pozycje faktury
            if zamowienia.produkty:
                for produkt in zamowienia.produkty:
                    try:
                        c.execute('INSERT INTO Produkty (nazwa, ilosc, cena, zamowienia_id) VALUES(?,?,?,?)',
                                        (produkt.nazwa, produkt.ilosc, produkt.cena, zamowienia.id)
                                )
                    except Exception as e:
                        #print "item add error:", e
                        raise RepositoryException('error adding zamowienia prod: %s, to zamowienia: %s' %
                                                    (str(produkt), str(zamowienia.id))
                                                )
        except Exception as e:
            #print "invoice add error:", e
            raise RepositoryException('error adding zamowienia %s' % str(zamowienia))

    def delete(self, zamowienia):

        try:
            c = self.conn.cursor()
            # usuń pozycje
            c.execute('DELETE FROM Produkty WHERE zamowienia_id=?', (zamowienia.id,))
            # usuń nagłowek
            c.execute('DELETE FROM Zamowienia WHERE id=?', (zamowienia.id,))

        except Exception as e:
            #print "invoice delete error:", e
            raise RepositoryException('error deleting zamowienia %s' % str(zamowienia))

    def getById(self, id):

        try:
            c = self.conn.cursor()
            c.execute("SELECT * FROM Zamowienia WHERE id=?", (id,))
            zam_row = c.fetchone()
            zamowienia = Zamowienia(id=id)
            if zam_row == None:
                Zamowienia=None
            else:
                zamowienia.data = zam_row[1]
                zamowienia.ilosc = zam_row[2]
                c.execute("SELECT * FROM Produkty WHERE zamowienia_id=? order by nazwa", (id,))
                zam_prods_rows = c.fetchall()
                prods_list = []
                for prod_row in zam_prods_rows:
                    prod = Produkt(nazwa=prod_row[0], ilosc=prod_row[1], cena=prod_row[2])
                    prods_list.append(prod)
                zamowienia.produkty=prods_list
        except Exception as e:

            raise RepositoryException('error getting by id zamowienia_id: %s' % str(id))
        return zamowienia

    def update(self, zamowienia):

        try:

            zam_oryg = self.getById(zamowienia.id)
            if zam_oryg != None:

                self.delete(zamowienia)
            self.add(zamowienia)

        except Exception as e:
            #print "invoice update error:", e
            raise RepositoryException('error updating zamowienia %s' % str(zamowienia))



if __name__ == '__main__':
    try:
        with ZamowieniaRepository() as zamowienia_repository:
            zamowienia_repository.add(
                Zamowienia(id = 1, data = datetime.now(),
                        produkty = [
                            Produkt(nazwa = "DB2015", ilosc = 300, cena = 25),
                            Produkt(nazwa = "FX8545", ilosc = 250, cena = 8),
                            Produkt(nazwa = "GH4584", ilosc = 801, cena = 10),
                        ]
                    )
                )
            zamowienia_repository.complete()
    except RepositoryException as e:
        print(e)

    print zamowieniaRepository().getById(1)

    try:
        with zamowieniaRepository() as zamowienia_repository:
            zamowienia_repository.update(
                Zamowienia(id = 1, data = datetime.now(),
                        Produkty = [
                            Produkt(nazwa = "JN2240", ilosc = 25, cena = 10),
                            Produkt(nazwa = "FX2542", ilosc = 150, cena = 12),
                            Produkt(nazwa = "OL2154", ilosc = 654, cena = 15),
                        ]
                    )
                )
            zamowienia_repository.complete()
    except RepositoryException as e:
        print(e)

    print ZamowieniaRepository().getById(1)

    # try:
    #     with ZamowieniaRepository() as zamowienia_repository:
    #         zamowienia_repository.delete( Zamowienia(id = 1) )
    #         zamowienia_repository.complete()
    # except RepositoryException as e:
    #     print(e)
