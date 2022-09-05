from rastadb import _db_recur, path
import sqlite3
from os import environ
from time import sleep
from random import uniform


def remove_like_value(db, table, vendor_like, url_like, commit_to_db=True):
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    sql = "DELETE FROM {} WHERE vendor = '{}' AND url LIKE '%{}%'".format(table, vendor_like, url_like)
    _db_recur(cursor, sql, 'remove_like_value')
    if commit_to_db:
        connection.commit()
    cursor.close()


def insert(db, table, to_insert, commit_to_db = True):
    """Inserts into sqlite db with the option:value schema"""
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    sql = 'INSERT OR REPLACE INTO {} VALUES {}'.format(table, to_insert)
    _db_recur(cursor, sql, 'insert')

    if commit_to_db:
        connection.commit()

    cursor.close()
    connection.close()


def _table_select(cursor, sql, recur_depth = 0):
    try:
        cursor.execute(sql)
        return cursor.fetchall()
    except Exception as e:
        if recur_depth <= 5:
            sleep(uniform(0.5, 4.5))
            recur_depth += 1
            print(f'Recur table select called. Depth: {recur_depth}')
            _table_select(cursor, sql, recur_depth = recur_depth)
        else:
            print('recur failed. SQL NOT EXECUTED:')
            print(f'{sql}')
            print(e)

        _table_select(cursor, sql)


def select_rows(db, table, column, option):
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    sql = 'SELECT * FROM {} WHERE {} LIKE \'%{}%\''.format(table, column, option)
    rows = _table_select(cursor, sql)
    cursor.close()
    connection.close()

    return rows


class RastaDealsDB:
    def __init__(self):
        self._dealcatcherdb = path + 'dealcatcher.db'
        self._rastadb = path + 'rastabot.db'
        self.vendors_table = 'vendors'
        self.internal_table = 'internal_deals'

    def get_vendors(self):
        vendor_list = select_rows(self._dealcatcherdb, self.vendors_table, 'website', 'http')
        return vendor_list

    def get_deals(self, vendor_acronym=None):
        if vendor_acronym:  # This is a call to show all deals for this vendor
            rows = select_rows(self._rastadb, self.internal_table, 'vendor', vendor_acronym)

        else:  # This is a search request, return every deal in existence
            rows = list()
            for acronym, name, website, thumbnail in self.get_vendors():
                vendor_rows = select_rows(self._rastadb, self.internal_table, 'vendor', acronym)
                for row in vendor_rows:
                    rows.append(row)

        return rows

    def new_deal(self, vendor_acronym, deal_tuple):
        name, url, image_url, amount, in_stock, description = deal_tuple
        insert_tuple = (vendor_acronym, name, url, image_url, amount, in_stock, description)
        insert(self._rastadb, self.internal_table, insert_tuple)  # Add the new record

    def expired_deal(self, vendor_acronym, deal_tuple):
        name, url, image_url, amount, in_stock, description = deal_tuple
        remove_like_value(self._rastadb, self.internal_table, vendor_acronym, url)


class DealCatcherDB:
    def __init__(self):
        self._dealcatcherdb = path + 'dealcatcher.db'
        self.vendors_table = 'vendors'
        self.active_table = 'active_deals'

    def get_vendors(self):
        vendor_list = select_rows(self._dealcatcherdb, self.vendors_table, 'website', 'http')
        return vendor_list

    def get_deals(self, vendor_acronym=None):
        if vendor_acronym:  # This is a call to show all deals for this vendor
            rows = select_rows(self._dealcatcherdb, self.active_table, 'vendor', vendor_acronym)

        else:  # This is a search request, return every deal in existence
            rows = list()
            for acronym, name, website, thumbnail in self.get_vendors():
                vendor_rows = select_rows(self._dealcatcherdb, self.active_table, 'vendor', acronym)
                for row in vendor_rows:
                    rows.append(row)

        return rows


dealcatcher_db = DealCatcherDB()
rastadeals_db = RastaDealsDB()
