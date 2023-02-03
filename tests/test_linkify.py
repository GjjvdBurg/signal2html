#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from signal2html.linkify import linkify


class TestLinkify(unittest.TestCase):
    _CASES = [
        (
            "Lorem ipsum www.example.com dolor sit amet",
            'Lorem ipsum <a href="http://www.example.com" target="_blank">www.example.com</a> dolor sit amet',
        ),
        (
            "Lorem ipsum example.com dolor sit amet",
            'Lorem ipsum <a href="http://example.com" target="_blank">example.com</a> dolor sit amet',
        ),
        (
            "Lorem ipsum https://www.example.com",
            'Lorem ipsum <a href="https://www.example.com" target="_blank">https://www.example.com</a>',
        ),
        ("lorem.ipsum.dolor sit amet", "lorem.ipsum.dolor sit amet"),
        (
            "Lorem ipsum www.example.yoga dolor sit amet",
            'Lorem ipsum <a href="http://www.example.yoga" target="_blank">www.example.yoga</a> dolor sit amet',
        ),
        (
            "Lorem ipsum https://timhein.ninja dolor sit amet",
            'Lorem ipsum <a href="https://timhein.ninja" target="_blank">https://timhein.ninja</a> dolor sit amet',
        ),
        (
            "Lorem ipsum test@example.com etc.",
            'Lorem ipsum <a href="mailto:test@example.com" target="_blank">test@example.com</a> etc.',
        ),
    ]

    def test_linkify(self):
        for message, expected in self._CASES:
            with self.subTest(message=message):
                self.assertEqual(expected, linkify(message))


if __name__ == "__main__":
    unittest.main()
