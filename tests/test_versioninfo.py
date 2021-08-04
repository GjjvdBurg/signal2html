#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from signal2html.versioninfo import VersionInfo


class TestVersionInfo(unittest.TestCase):
    def test_init(self):
        vi = VersionInfo(10)
        self.assertEqual(vi.version, 10)

    def test_is_addressbook_using_rids(self):
        vi = VersionInfo(10)
        self.assertFalse(vi.is_addressbook_using_rids())
        vi = VersionInfo(24)
        self.assertTrue(vi.is_addressbook_using_rids())
        vi = VersionInfo(110)
        self.assertTrue(vi.is_addressbook_using_rids())

    def test_get_reactions_query_column(self):
        vi = VersionInfo(18)
        self.assertEqual(vi.get_reactions_query_column(), "''")
        vi = VersionInfo(37)
        self.assertEqual(vi.get_reactions_query_column(), "reactions")
        vi = VersionInfo(80)
        self.assertEqual(vi.get_reactions_query_column(), "reactions")

    def test_are_mentions_supported(self):
        vi = VersionInfo(18)
        self.assertFalse(vi.are_mentions_supported())
        vi = VersionInfo(68)
        self.assertTrue(vi.are_mentions_supported())
        vi = VersionInfo(100)
        self.assertTrue(vi.are_mentions_supported())

    def test_get_quote_mentions_query_column(self):
        vi = VersionInfo(18)
        self.assertEqual(vi.get_quote_mentions_query_column(), "''")
        vi = VersionInfo(68)
        self.assertEqual(
            vi.get_quote_mentions_query_column(), "quote_mentions"
        )
        vi = VersionInfo(100)
        self.assertEqual(
            vi.get_quote_mentions_query_column(), "quote_mentions"
        )

    def test_get_thread_recipient_id_column(self):
        vi = VersionInfo(18)
        self.assertEqual(vi.get_thread_recipient_id_column(), "recipient_ids")
        vi = VersionInfo(108)
        self.assertEqual(
            vi.get_thread_recipient_id_column(), "thread_recipient_id"
        )
        vi = VersionInfo(110)
        self.assertEqual(
            vi.get_thread_recipient_id_column(), "thread_recipient_id"
        )


if __name__ == "__main__":
    unittest.main()
