# -*- coding: utf-8 -*-

"""Various exceptions

License: See LICENSE file.

"""


class DatabaseNotFoundError(FileNotFoundError):
    pass


class DatabaseVersionNotFoundError(FileNotFoundError):
    pass


class DatabaseEmptyError(ValueError):
    def __init__(self):
        super().__init__(
            "Database is empty, something must have gone wrong exporting or "
            "unpacking the Signal backup."
        )
