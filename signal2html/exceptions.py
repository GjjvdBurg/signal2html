# -*- coding: utf-8 -*-

"""Various exceptions

"""


class DatabaseNotFound(Exception):
    pass


class DatabaseVersionNotFound(Exception):
    pass


class DatabaseVersionMismatch(Exception):
    pass
