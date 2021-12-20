#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Class grouping version-specific information from the signal database.

This file in the Signal source can be used to determine when features were 
introduced:

    https://github.com/signalapp/Signal-Android/blob/master/app/src/main/java/org/thoughtcrime/securesms/database/helpers/SQLCipherOpenHelper.java

License: See LICENSE file.

"""

import logging

logger = logging.getLogger(__name__)


class VersionInfo(object):
    def __init__(self, version):
        self.version = int(version)
        logger.info(f"Found Signal database version: {version}.")

    def is_tested_version(self) -> bool:
        """Returns whether the database version has been tested.

        Testing and pull requests welcome."""

        return self.version in [18, 23, 65, 80, 89, 110]

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

    def get_quote_mentions_query_column(self) -> str:
        """Returns a SQL expression to retrieve quote mentions in MMS messages."""

        return "quote_mentions" if self.are_mentions_supported() else "''"

    def get_viewed_receipt_count_column(self) -> str:
        """Returns a SQL expression to retrieve the viewed receipt count of attachments of MMS messages."""

        return "viewed_receipt_count" if self.version >= 83 else "'0'"

    def get_thread_recipient_id_column(self) -> str:
        """Returns SQL expression to retrieve recipient id from thread table"""
        return (
            "thread_recipient_id" if self.version >= 108 else "recipient_ids"
        )
