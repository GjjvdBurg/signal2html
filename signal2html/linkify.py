# -*- coding: utf-8 -*-

"""Module for linkifying urls in messages

License: See LICENSE file

"""

import logging

from linkify_it import LinkifyIt
from linkify_it.tlds import TLDS

logger = logging.getLogger(__name__)


class Linkify:
    def __init__(self):
        self._linkifier = LinkifyIt().tlds(TLDS)

    def linkify(self, message: str) -> str:
        """Replace text URLs in message with HTML links"""
        # Pre-test first for efficiency
        if not self._linkifier.pretest(message):
            return message

        # Test if a link is present
        if not self._linkifier.test(message):
            return message

        # Find links in message
        matches = self._linkifier.match(message)
        if not matches:
            return message

        logger.debug(f"Replacing urls in message:\n{message}")

        # Construct new message
        new_message = ""
        idx = 0
        for match in matches:
            new_message += message[idx : match.index]
            new_message += (
                f'<a href={match.url}" target="_blank">{match.raw}</a>'
            )
            idx = match.last_index
        new_message += message[idx:]

        logger.debug(f"Replaced urls in message:\n{new_message}")
        return new_message
