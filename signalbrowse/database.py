# -*- coding: utf-8 -*-

"""Functionality for working with the Sqlite database

Author: Gertjan van den Burg

"""

import sqlite3

def open_database(db_file):
    conn = sqlite3.connect(db_file)
    return conn.cursor()



