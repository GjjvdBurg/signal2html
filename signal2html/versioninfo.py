#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Class grouping version-specific information from the signal database.

License: See LICENSE file.
"""


class VersionInfo(object):
    def __init__(self, version):
        self.version = int(version)

    def is_tested_version(self) -> bool:
        """Returns whether the database version has been tested.

        Testing and pull requests welcome."""

        return self.version in [18, 23, 65, 80, 89]

    def is_addressbook_using_rids(self) -> bool:
        """Returns whether the contacts are structured using recipient IDs.

        Previous versions referred to contacts using their phone numbers or a
        special group ID."""

        return self.version >= 24

    def get_reactions_query_column(self) -> str:
        """Returns a SQL expression to retrieve reactions to MMS messages."""

        return "reactions" if self.version >= 37 else "''"

    def are_mentions_supported(self) -> bool:
        """Returns whether the mentions table is present."""

        return self.version >= 68
