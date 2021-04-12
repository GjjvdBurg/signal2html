#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Models for storing Signal backup objects.

These are heavily inspired by the database models of the Signal Android app, 
but only the necessary fields are kept.

Author: G.J.J. van den Burg
License: See LICENSE file.
Copyright: 2020, G.J.J. van den Burg

"""

from abc import ABCMeta
from dataclasses import dataclass, field
from typing import List
from re import sub
from unicodedata import normalize

@dataclass
class RecipientId:
    _id: str  # phone number (?)

    def __hash__(self):
        return hash(self._id)


@dataclass
class Quote:
    _id: int
    author: RecipientId
    text: str


@dataclass
class Attachment:
    contentType: str
    fileName: str
    voiceNote: bool
    width: int
    height: int
    quote: bool
    unique_id: str


@dataclass
class Recipient:
    recipientId: RecipientId
    name: str
    color: str
    isgroup: bool
    phone: str

    def __hash__(self):
        return hash(self.recipientId)


@dataclass
class DisplayRecord(metaclass=ABCMeta):
    addressRecipient: Recipient  # Recipient corresponding to address field
    recipient: Recipient
    dateSent: int
    dateReceived: int
    threadId: int
    body: str
    _type: int


@dataclass
class MessageRecord(DisplayRecord):
    _id: int


@dataclass
class MMSMessageRecord(MessageRecord):
    quote: Quote
    attachments: List[Attachment]


@dataclass
class SMSMessageRecord(MessageRecord):
    pass


@dataclass
class Thread:
    _id: int
    recipient: Recipient
    mms: List[MMSMessageRecord] = field(default_factory=lambda: [])
    sms: List[SMSMessageRecord] = field(default_factory=lambda: [])

    @property
    def sanephone(self):
        """Return a sanitized phone number suitable for use as filename, and fallback on rid.

        NOTE: Phone numbers can be alphanumerical characters especially coming over SMS
        Different strings can still clash in principle if they sanitize to the same string.
        """
        if self.recipient.phone:
            return self._sanitize(self.recipient.phone)
        else:
            return '#' + self.recipient.recipientId._id

    @property
    def name(self):
        """Return the raw name or other useful identifier, suitable for display."""
        return self.recipient.name.strip()

    @property
    def sanename(self):
        """Return a sanitized name or other useful identifier, suitable for use as filename, and fallback on rid."""
        if self.recipient.name:
            return self._sanitize(self.recipient.name)
        else:
            return '#' + self.recipient.recipientId._id

    def _sanitize(self, text):
        """Sanitize text to use as filename"""
        clean = normalize('NFKC', text.strip())
        clean = clean.lstrip(".#")
        clean = sub('[^]\\w!@#$%^&\'`.=+{}~()[-]', '_', clean)
        return clean

