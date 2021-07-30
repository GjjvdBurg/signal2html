# -*- coding: utf-8 -*-

"""Module to organize various database queries

This file is part of signal2html.
License: See LICENSE file.

"""

import sqlite3

from types import SimpleNamespace

from typing import Any
from typing import List

from .versioninfo import VersionInfo


class Row(SimpleNamespace):
    pass


class Database:
    def __init__(self, database_file: str, version_info: VersionInfo):
        self._database_file = database_file
        self._version_info = version_info

    def get_threads(self) -> List[Row]:
        """Retrieve the threads from the database"""
        recipient_id_expr = self._version_info.get_thread_recipient_id_column()
        query = (
            "SELECT _id AS thread_id, "
            f"{recipient_id_expr} AS recipient_id "
            "FROM thread"
        )
        return self._execute(query)

    # TODO: Add all database queries as methods of this class

    def _execute(self, query: str, **kwargs) -> List[Row]:
        """Execute the given query with the provided keyword arguments"""
        connection = sqlite3.connect(self._database_file)
        connection.row_factory = simple_namespace_factory
        cursor = connection.cursor()

        cursor.execute(query, kwargs)
        rows = cursor.fetchall()

        cursor.close()
        connection.close()
        return rows


def simple_namespace_factory(cursor: sqlite3.Cursor, row: List[Any]) -> Row:
    """Returns sqlite rows as named tuples"""
    fields = [col[0] for col in cursor.description]
    items = {k: v for k, v in zip(fields, row)}
    return Row(**items)
